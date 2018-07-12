package main

import (
	"fmt"
	"net/http"
)

func DownloadHandler(w http.ResponseWriter, r *http.Request) {
	imageid := r.URL.Query().Get("fn") //vars["imgid"]
	if len([]rune(imageid)) == 0 {
		w.Write([]byte("Error:ImageID incorrect."))
		return
	}
	imgpath := ImageID2Path(imageid)
	fmt.Println("imgpath" + imgpath)
	if !FileExist(imgpath) {
		fmt.Println("Error:Image Not Found imgpath is " + imgpath)
		w.Write([]byte("Error:Image Not Found."))
		return
	}
	http.ServeFile(w, r, imgpath)
}
