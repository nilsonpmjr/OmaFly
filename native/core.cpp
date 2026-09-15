// Normalized LIF reference. No background threads, allocations or busy waits in step().
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <vector>

struct Circuit {
    int n;
    float vm_decay, syn_decay, rate_decay;
    std::vector<int> offset, pre;
    std::vector<float> weights, voltage, syn, rate;
    std::vector<uint8_t> spikes, next, refractory;
    Circuit(int size, int edges, const int* off, const int* source, const float* w)
        : n(size), vm_decay(std::exp(-1.f/20.f)), syn_decay(std::exp(-1.f/5.f)),
          rate_decay(std::exp(-1.f/30.f)), offset(off, off+size+1),
          pre(source, source+edges), weights(w, w+edges), voltage(size), syn(size),
          rate(size), spikes(size), next(size), refractory(size) {}
};

extern "C" {
void* ff_create(int n, int edges, const int* offsets, const int* pre, const float* weights) {
    if (n <= 0 || n > 100000 || edges < 0 || !offsets || !pre || !weights) return nullptr;
    if (offsets[0] != 0 || offsets[n] != edges) return nullptr;
    for (int i=0; i<n; ++i) if (offsets[i] > offsets[i+1] || offsets[i]<0) return nullptr;
    for (int i=0; i<edges; ++i) if (pre[i]<0 || pre[i]>=n || !std::isfinite(weights[i])) return nullptr;
    try { return new Circuit(n, edges, offsets, pre, weights); } catch (...) { return nullptr; }
}
void ff_destroy(void* ptr) { delete static_cast<Circuit*>(ptr); }
void ff_reset(void* ptr) {
    auto& c=*static_cast<Circuit*>(ptr);
    std::fill(c.voltage.begin(),c.voltage.end(),0);
    std::fill(c.syn.begin(),c.syn.end(),0);
    std::fill(c.rate.begin(),c.rate.end(),0);
    std::fill(c.spikes.begin(),c.spikes.end(),0);
    std::fill(c.refractory.begin(),c.refractory.end(),0);
}
void ff_step(void* ptr, const float* input, int steps, float* output) {
    auto& c=*static_cast<Circuit*>(ptr);
    for (int step=0;step<steps;++step) {
        for (int i=0;i<c.n;++i) {
            float incoming=0;
            for(int j=c.offset[i];j<c.offset[i+1];++j) incoming+=c.weights[j]*c.spikes[c.pre[j]];
            c.syn[i]=c.syn[i]*c.syn_decay+incoming;
            c.next[i]=0;
            if(c.refractory[i]) --c.refractory[i];
            else {
                c.voltage[i]=std::max(0.f,c.voltage[i]*c.vm_decay+input[i]+c.syn[i]);
                if(c.voltage[i]>=1.f) {c.next[i]=1;c.voltage[i]=0;c.refractory[i]=2;}
            }
            c.rate[i]=c.rate[i]*c.rate_decay+float(c.next[i])*1000.f*(1.f-c.rate_decay);
        }
        c.spikes.swap(c.next);
    }
    std::copy(c.rate.begin(),c.rate.end(),output);
}
}
