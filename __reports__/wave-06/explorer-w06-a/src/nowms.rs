fn main(){let t=std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_secs_f64()*1000.0;println!("{:.3}",t);}
