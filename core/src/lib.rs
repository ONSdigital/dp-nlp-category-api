use std::fs::{File, OpenOptions};
use std::io::{BufReader, BufWriter};
use finalfusion::io::WriteEmbeddings;
use numpy::PyArray;
use numpy::ndarray::Ix1;

use finalfusion::prelude::*;
use pyo3::prelude::*;
use pyo3::PyErr;
use pyo3::exceptions::PyIOError;

#[pyclass]
struct FfModel {
    embeddings: Embeddings<VocabWrap, StorageWrap>
}

#[pymethods]
impl FfModel {
    #[new]
    pub fn __new__(embeddings_path: &str) -> Self {
        let f = File::open(embeddings_path).expect("Embedding file missing, run fetch-data.sh");
        FfModel {
            embeddings: Embeddings::mmap_embeddings(&mut BufReader::new(f)).unwrap()
        }
    }

    fn get_dims(
        self_: PyRef<Self>
    ) -> usize {
        self_.embeddings.dims()
    }

    fn load_embedding(
        self_: PyRef<Self>,
        sentence: &str,
        a: &PyArray<f32, Ix1>
    ) -> bool {
        let success: bool;
        unsafe {
            let arr = a.as_array_mut();
            success = self_.embeddings.embedding_into(
                sentence,
                arr
            );
        }
        success
    }

    fn eval(self_: PyRef<Self>, haystack: &str) -> PyResult<()> {
        if let Some(embedding) = self_.embeddings.embedding(haystack) {
             println!("{:#?}", embedding);
        }
        Ok(())
    }
}

fn handle_error(error_message: String) -> PyErr {
    let gil = Python::acquire_gil();
    let py = gil.python();
    PyIOError::new_err(error_message).restore(py);
    return PyErr::fetch(py);
}

#[pyfunction]
fn build_model(input_path: String, output_path: String) -> PyResult<()> {
    // Read the embeddings.
    println!("Reading fasttext embeddings");

    let file;
    match File::open(input_path) {
        Ok(f) => { file = f }
        Err(e) => { return Err(handle_error(e.to_string())) }
    };
    let mut reader = BufReader::new(file);
    let embeddings;
    match Embeddings::read_fasttext(&mut reader) {
        Ok(e) => { embeddings = e }
        Err(e) => { return Err(handle_error(e.to_string())) }
    };

    println!("Writing fasttext embeddings");

    let outfile = OpenOptions::new()
                .read(true)
                .write(true)
                .create(true)
                .open(output_path);
    let mut writer;
    match outfile {
        Ok(outfile) => { writer = BufWriter::new(outfile) }
        Err(e) => { return Err(handle_error(e.to_string())) }
    };

    match embeddings.write_embeddings(&mut writer) {
        Ok(_embeddings) => {}
        Err(e) => { return Err(handle_error(e.to_string())) }
    };

    println!("Done");

    Ok(())
}

#[pymodule]
fn ff_fasttext(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_class::<FfModel>()?;
    m.add_function(wrap_pyfunction!(build_model, m)?)?;

    Ok(())
}
