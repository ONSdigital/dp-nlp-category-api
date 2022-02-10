use std::fs::File;
use std::io::BufReader;

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

    fn eval(self_: PyRef<Self>, haystack: &str) -> PyResult<()> {
        if let Some(embedding) = self_.embeddings.embedding(haystack) {
             println!("{:#?}", embedding);
        }
        Ok(())
    }
}

#[pymodule]
fn _ff_fasttext(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_class::<FfModel>()?;

    Ok(())
}
