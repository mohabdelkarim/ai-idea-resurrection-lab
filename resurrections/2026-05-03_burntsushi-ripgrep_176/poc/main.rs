use grep_matcher::Matcher;
use grep_regex::RegexMatcher;
use grep_searcher::Searcher;
use grep_searcher::sinks::UTF8;

fn main() {
    // A multiline pattern: match from "listeners" up to "click" across newlines
    // The (?s) flag makes `.` match newlines as well
    let pattern = r"(?s)listeners.+?click";

    let text = b"listeners: {
    foo: ...
    click: ....
}";

    let matcher = RegexMatcher::new(pattern).expect("Invalid regex pattern");

    Searcher::new()
        .search_slice(
            &matcher,
            text,
            UTF8(|line_number, line| {
                println!("Match on line {}: {}", line_number, line.trim_end());
                Ok(true)
            }),
        )
        .expect("Search failed");

    println!("Done.");
}
