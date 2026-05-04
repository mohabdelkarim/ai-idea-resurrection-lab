
   use std::env;
   use std::fs::File;
   use std::io::{BufRead, BufReader};
   use std::path::Path;

   struct Ripgrep {
       max_line_length: usize,
   }

   impl Ripgrep {
       fn new(max_line_length: usize) -> Self {
           Ripgrep { max_line_length }
       }

       fn truncate_line(&self, line: &str) -> String {
           if line.len() > self.max_line_length {
               let mut truncated_line = line.chars().take(self.max_line_length).collect::<String>();
               truncated_line.push_str("...");
               truncated_line
           } else {
               line.to_string()
           }
       }

       fn search(&self, file_path: &str) -> Vec<String> {
           let file = File::open(file_path).unwrap();
           let reader = BufReader::new(file);
           let mut results = Vec::new();

           for line in reader.lines() {
               let line = line.unwrap();
               let truncated_line = self.truncate_line(&line);
               results.push(truncated_line);
           }

           results
       }
   }

   fn main() {
       let args: Vec<String> = env::args().collect();
       let max_line_length: usize = args[1].parse().unwrap();
       let file_path = &args[2];

       let ripgrep = Ripgrep::new(max_line_length);
       let results = ripgrep.search(file_path);

       for result in results {
           println!("{}", result);
       }
   }
   