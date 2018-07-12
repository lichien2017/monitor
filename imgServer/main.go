package main

import (
	"fmt"
	"log"
	"net/http"
)

func main() {
	fmt.Println("Quick Image Server.")
	LoadConf()
	// r := mux.NewRouter()
	// r.HandleFunc("/", HomeHandler).Methods("GET")
	// r.HandleFunc("/",UploadHandler).Methods("POST")
	http.HandleFunc("/filename", DownloadHandler)
	err := http.ListenAndServe(conf.ListenAddr, nil)
	if err != nil {
		log.Fatal("ListenAndServe error: ", err)
	}
}
