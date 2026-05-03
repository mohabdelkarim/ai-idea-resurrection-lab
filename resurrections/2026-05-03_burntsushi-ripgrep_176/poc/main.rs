
   ```rust
   use regex::Regex;
   use ripgrep::Searcher;
   use ripgrep::SearcherBuilder;

   struct MultilineSearcher {
       regex: Regex,
       searcher: Searcher,
   }

   impl MultilineSearcher {
       fn new(pattern: &str) -> Self {
           let regex = Regex::new(pattern).unwrap();
           let searcher = SearcherBuilder::new().build().unwrap();
           MultilineSearcher { regex, searcher }
       }

       fn search(&self, text: &str) -> Vec<(usize, usize)> {
           let mut matches = Vec::new();
           for (start, end) in self.regex.find_iter(text) {
               matches.push((start, end));
           }
           matches
       }
   }

   fn main() {
       let searcher = MultilineSearcher::new("(?s)listeners.+click");
       let text = "listeners: {
           foo: ...
           click: ....
       }";
       let matches = searcher.search(text);
       for (start, end) in matches {
           println!("Match found at ({}, {})", start, end);
       }
   }
   ```