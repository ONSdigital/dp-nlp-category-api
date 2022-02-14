use std::fs::File;
use std::io::BufReader;
use numpy::PyArray;
use numpy::ndarray::Ix1;

use finalfusion::prelude::*;
use pyo3::prelude::*;

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

#[pymodule]
fn ff_fasttext(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_class::<FfModel>()?;

    Ok(())
}
