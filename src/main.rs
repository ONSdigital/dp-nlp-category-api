use std::fs::{File, OpenOptions};
use std::io::{BufReader, BufWriter};

use finalfusion::prelude::*;
use finalfusion::io::WriteEmbeddings;

fn main() {
    // Read the embeddings.
    println!("Reading fasttext embeddings");

    let mut reader = BufReader::new(File::open("test_data/wiki-news-300d-1M.vec").unwrap());
    let embeddings = Embeddings::read_fasttext(&mut reader).unwrap();

    println!("Writing fasttext embeddings");

    let file = OpenOptions::new()
                .read(true)
                .write(true)
                .create(true)
                .open("test_data/wiki-news-300d-1M.fifu")
                .unwrap();
    let mut writer = BufWriter::new(file);
    embeddings.write_embeddings(&mut writer).unwrap();


    println!("Done");
}

/*
use finalfusion::vocab::{Vocab, WordIndex};

const OPQ_EMBEDDINGS: &str = "benches/de-structgram-20190426-opq.fifu";

fn read_embeddings() -> Embeddings<VocabWrap, StorageWrap> {
        let f = File::open(OPQ_EMBEDDINGS).expect("Embedding file missing, run fetch-data.sh");
            Embeddings::read_embeddings(&mut BufReader::new(f)).unwrap()
}

fn mmap_embeddings() -> Embeddings<VocabWrap, StorageWrap> {
        let f = File::open(OPQ_EMBEDDINGS).expect("Embedding file missing, run fetch-data.sh");
            Embeddings::mmap_embeddings(&mut BufReader::new(f)).unwrap()
}


use std::fs::File;
use std::io::BufReader;

use finalfusion::prelude::*;


*/
