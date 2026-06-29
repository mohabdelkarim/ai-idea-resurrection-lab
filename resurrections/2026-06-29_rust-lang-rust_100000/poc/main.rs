use std::collections::HashMap;
use std::fs::File;
use std::io::{BufReader, BufRead};
use std::path::Path;

fn main() -> std::io::Result<()> {
    let file = File::open("issues.txt")?;
    let reader = BufReader::new(file);
    let mut issues: HashMap<String, usize> = HashMap::new();
    for line in reader.lines() {
        let line = line?;
        if line.starts_with("Issue #") {
            let issue_number = line.trim_start_matches("Issue #").trim_start_matches(" ");
            *issues.entry(issue_number.to_string()).or_insert(0) += 1;
        }
    }
    for (issue, count) in issues {
        println!("Issue {}: {}", issue, count);
    }
    Ok(())
}

// Error handling example
fn handle_error(err: std::io::Error) {
    eprintln!("Error: {}", err);
}

// A simple function to demonstrate Rust's pattern matching
fn describe_color(color: &str) {
    match color {
        "red" => println!("The color is red"),
        "green" => println!("The color is green"),
        _ => println!("The color is unknown"),
    }
}

// A simple function to calculate the area of a rectangle
fn calculate_area(length: f64, width: f64) -> f64 {
    length * width
}

// A struct example
struct Person {
    name: String,
    age: u32,
}

impl Person {
    fn new(name: String, age: u32) -> Person {
        Person { name, age }
    }
    fn greet(&self) {
        println!("Hello, my name is {} and I am {} years old.", self.name, self.age);
    }
}

// Enum example
enum Day {
    Monday,
    Tuesday,
    Wednesday,
    Thursday,
    Friday,
    Saturday,
    Sunday,
}

impl Day {
    fn is_weekend(&self) -> bool {
        match self {
            Day::Saturday | Day::Sunday => true,
            _ => false,
        }
    }
}

// A simple trait example
trait Animal {
    fn sound(&self);
}

struct Dog;

impl Animal for Dog {
    fn sound(&self) {
        println!("Woof!");
    }
}

// A simple function that uses a trait object
fn make_sound(animal: &dyn Animal) {
    animal.sound();
}

// Testing the code
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_calculate_area() {
        assert_eq!(calculate_area(10.0, 5.0), 50.0);
    }
    #[test]
    fn test_person() {
        let person = Person::new("John".to_string(), 30);
        assert_eq!(person.name, "John");
        assert_eq!(person.age, 30);
    }
}