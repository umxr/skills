use std::collections::HashMap;
use std::net::SocketAddr;

pub struct Router {
    routes: HashMap<String, SocketAddr>,
}

impl Router {
    pub fn new() -> Self {
        Self { routes: HashMap::new() }
    }
    pub fn add(&mut self, topic: &str, addr: SocketAddr) {
        self.routes.insert(topic.to_string(), addr);
    }
    pub fn lookup(&self, topic: &str) -> Option<&SocketAddr> {
        self.routes.get(topic)
    }
}
