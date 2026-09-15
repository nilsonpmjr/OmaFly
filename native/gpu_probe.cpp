// Bounded HIP experiment. One workgroup keeps state resident across neural substeps.
// Deliberately excluded from the desktop runtime until energy/latency justify it.
#include <hip/hip_runtime.h>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <fstream>
#include <thread>
#include <vector>

#define HIP_CHECK(x) do { auto hip_result=(x); if(hip_result!=hipSuccess) {std::fprintf(stderr,"%s: %s\n",#x,hipGetErrorString(hip_result));return 2;} }while(0)

__global__ void advance(int n, const int* off, const int* pre, const float* w,
                        float* voltage,float* syn,float* rate,unsigned char* refractory,
                        unsigned char* previous,const float* input,int steps) {
    __shared__ unsigned char spikes[1024];
    __shared__ unsigned char next[1024];
    int i=threadIdx.x;
    if(i<n)spikes[i]=previous[i];
    __syncthreads();
    const float vd=expf(-1.f/20.f),sd=expf(-1.f/5.f),rd=expf(-1.f/30.f);
    for(int s=0;s<steps;++s) {
        if(i<n) {
            float incoming=0;
            for(int j=off[i];j<off[i+1];++j) incoming+=w[j]*spikes[pre[j]];
            syn[i]=syn[i]*sd+incoming; next[i]=0;
            if(refractory[i])--refractory[i];
            else {
                voltage[i]=fmaxf(0.f,voltage[i]*vd+input[i]+syn[i]);
                if(voltage[i]>=1.f){next[i]=1;voltage[i]=0;refractory[i]=2;}
            }
            rate[i]=rate[i]*rd+float(next[i])*1000.f*(1.f-rd);
        }
        __syncthreads();
        if(i<n)spikes[i]=next[i];
        __syncthreads();
    }
    if(i<n)previous[i]=spikes[i];
}

int main(int argc,char** argv) {
    if(argc!=3){std::fprintf(stderr,"usage: gpu-probe INPUT.bin OUTPUT.bin\n");return 1;}
    std::ifstream f(argv[1],std::ios::binary);
    int n=0,e=0;f.read((char*)&n,4);f.read((char*)&e,4);
    if(n<=0||n>1024||e<0||e>1000000)return 1;
    std::vector<int> off(n+1),pre(e);
    std::vector<float> w(e),input(n),output(n);
    f.read((char*)off.data(),4*(n+1));f.read((char*)pre.data(),4*e);
    f.read((char*)w.data(),4*e);f.read((char*)input.data(),4*n);
    if(!f || off[0]!=0 || off[n]!=e)return 1;
    for(int i=0;i<n;++i)if(off[i]<0||off[i]>off[i+1])return 1;
    for(int p:pre)if(p<0||p>=n)return 1;
    int count=0;HIP_CHECK(hipGetDeviceCount(&count));if(!count)return 3;
    hipDeviceProp_t prop;HIP_CHECK(hipGetDeviceProperties(&prop,0));
    int *doff,*dpre;float *dw,*dv,*ds,*dr,*di;unsigned char *drefr,*dprev;
    HIP_CHECK(hipMalloc(&doff,4*(n+1)));HIP_CHECK(hipMalloc(&dpre,4*e));
    HIP_CHECK(hipMalloc(&dw,4*e));HIP_CHECK(hipMalloc(&dv,4*n));
    HIP_CHECK(hipMalloc(&ds,4*n));HIP_CHECK(hipMalloc(&dr,4*n));
    HIP_CHECK(hipMalloc(&di,4*n));HIP_CHECK(hipMalloc(&drefr,n));HIP_CHECK(hipMalloc(&dprev,n));
    HIP_CHECK(hipMemcpy(doff,off.data(),4*(n+1),hipMemcpyHostToDevice));
    HIP_CHECK(hipMemcpy(dpre,pre.data(),4*e,hipMemcpyHostToDevice));
    HIP_CHECK(hipMemcpy(dw,w.data(),4*e,hipMemcpyHostToDevice));
    HIP_CHECK(hipMemset(dv,0,4*n));HIP_CHECK(hipMemset(ds,0,4*n));
    HIP_CHECK(hipMemset(dr,0,4*n));HIP_CHECK(hipMemset(drefr,0,n));HIP_CHECK(hipMemset(dprev,0,n));
    auto begin=std::chrono::steady_clock::now();double active_ms=0;
    // 5 seconds, 25Hz, 40 neural ms/cycle. Sleep between cycles; no throughput stress test.
    for(int i=0;i<125;++i) {
        auto tick=std::chrono::steady_clock::now();
        HIP_CHECK(hipMemcpy(di,input.data(),4*n,hipMemcpyHostToDevice));
        hipLaunchKernelGGL(advance,dim3(1),dim3((n+63)/64*64),0,0,n,doff,dpre,dw,dv,ds,dr,drefr,dprev,di,40);
        HIP_CHECK(hipGetLastError());
        HIP_CHECK(hipMemcpy(output.data(),dr,4*n,hipMemcpyDeviceToHost));
        active_ms+=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-tick).count();
        std::this_thread::sleep_until(begin+std::chrono::milliseconds((i+1)*40));
    }
    std::ofstream out(argv[2],std::ios::binary);out.write((char*)output.data(),4*n);
    std::printf("{\"device\":\"%s\",\"cycles\":125,\"neural_ms\":5000,\"active_ms_per_cycle\":%.6f}\n",prop.name,active_ms/125);
    HIP_CHECK(hipFree(doff));HIP_CHECK(hipFree(dpre));HIP_CHECK(hipFree(dw));HIP_CHECK(hipFree(dv));
    HIP_CHECK(hipFree(ds));HIP_CHECK(hipFree(dr));HIP_CHECK(hipFree(di));HIP_CHECK(hipFree(drefr));HIP_CHECK(hipFree(dprev));
    return 0;
}
