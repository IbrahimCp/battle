package main

import (
	"net/http"
)

func (app *application) health(w http.ResponseWriter, r *http.Request) {
	data := map[string]string{
		"status":  "available",
		"version": "1.0.0",
	}

	app.writeJSON(w, 200, data)
}
