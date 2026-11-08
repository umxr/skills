use criterion::{criterion_group, criterion_main, Criterion};

fn bench(c: &mut Criterion) {
    c.bench_function("encode", |b| b.iter(|| {
        let mut buf = bytes::BytesMut::new();
        relay_core::frame::encode(b"payload", &mut buf);
    }));
}

criterion_group!(benches, bench);
criterion_main!(benches);
