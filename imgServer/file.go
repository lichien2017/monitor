package main

import (
	"fmt"
	"os"
)

func ImageID2Path(imageid string) string {
	return fmt.Sprintf("%s%s", conf.Storage, imageid)
	//return fmt.Sprintf("%s/%s/%s/%s/%s/%s/%s/%s/%s.jpg",conf.Storage,imageid[0:2],imageid[2:4],imageid[4:6],imageid[6:8],imageid[8:10],imageid[10:12],imageid[12:14],imageid[14:16])
}

func FileExist(filename string) bool {
	if _, err := os.Stat(filename); err != nil {
		return false
	} else {
		return true
	}
}
