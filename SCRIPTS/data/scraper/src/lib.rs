use std::io::BufReader;
use std::fs::read_dir;
use std::io::BufRead;
use std::path::Path;
use std::ffi::OsStr;
use std::io::Error;
use std::fs::File;
use pyo3::prelude::*;

// some functionalities for data generating
// extract random fragments from proteins collection

static AA_CODES: &'static [char] = &['A', 'R', 'N', 'D', 'C', 'Q', 'E', 'G', 'H', 'I', 'L', 'K', 'M', 'F', 'P', 'S', 'T', 'W', 'Y', 'V'];
static SS_CODES: &'static [char] = &['H', 'E', 'C'];

#[pyfunction]
pub fn check_if_correct(line: &str) -> bool
{
    let mut ok = true;
    // split line into vector of strings
    let elements: Vec<&str> = line.split_whitespace().collect();
    // get amino acids and secondary structure vectors
    let aa: Vec<char> = elements[4].chars().collect();
    let ss: Vec<char> = elements[5].chars().collect();
    for aa in aa
    {
        if !AA_CODES.contains(&aa)
        {
            ok = false;
        }
    }
    for ss in ss
    {
        if !SS_CODES.contains(&ss)
        {
            ok = false;
        }
    }
    ok
}

#[pyfunction]
pub fn get_extension(file: &str) -> Option<&str>
{
    Path::new(file).extension().and_then(OsStr::to_str)
}

#[pyfunction]
pub fn collect_files(directory: &str) -> Vec<String>
{
    let all = read_dir(directory).unwrap();
    let mut files = Vec::new();
    for item in all
    {
        let file = item.unwrap().path().display().to_string();
        if Some(get_extension(&file)) == Some(Some("dat"))
        {
            files.push(file);
        }
    }
    files
}

#[pyfunction]
pub fn read_lines(file: &str) -> Vec<Result<String, Error>>
{
    // also check each line 
    let stream  = File::open(file).expect("Cannot open file");
    let reader = BufReader::new(stream);
    let mut lines = Vec::new();
    for line in reader.lines()
    {
        let ok = check_if_correct(&line.as_ref().unwrap().to_string());
        if ok == true
        {
            lines.push(line);
        }
    }
    lines
}

#[pymodule]
fn scraper(_: Python, m: &PyModule) -> PyResult<()>
{
    Ok(())
}
