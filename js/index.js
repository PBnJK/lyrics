const db = JSON.parse(document.getElementById("db").textContent);

const checkAlbumMatches = (album, term) => {
  if (term === "") {
    return true;
  }

  const regex = new RegExp(term, "i");
  if (regex.test(album.album)) {
    return true;
  }

  for (const artist of album.artist) {
    if (regex.test(artist)) {
      return true;
    }
  }

  for (const genre of album.genre) {
    if (regex.test(genre)) {
      return true;
    }
  }

  return regex.test(album.year);
};

const refreshTable = (term) => {
  const table = document.getElementById("tbody");
  while (table.firstChild) {
    table.removeChild(table.lastChild);
  }

  for (const key in db) {
    const data = db[key];
    if (!checkAlbumMatches(data, term)) {
      continue;
    }

    const tr = document.createElement("tr");

    const albumField = document.createElement("td");
    const artistField = document.createElement("td");
    const genreField = document.createElement("td");
    const yearField = document.createElement("td");

    albumField.innerText = data.album;
    artistField.innerText = data.artist.join(", ");
    genreField.innerText = data.genre.join(", ");

    yearField.innerText = data.year;
    yearField.classList.add("td-year");

    tr.appendChild(albumField);
    tr.appendChild(artistField);
    tr.appendChild(genreField);
    tr.appendChild(yearField);

    tr.setAttribute("onclick", `window.location='${key + ".html"}'`);
    tr.classList.add("clickable");

    table.appendChild(tr);
  }
};

refreshTable("");

const search = document.getElementById("search");
search.addEventListener("input", () => {
  console.log("hi");
  refreshTable(search.value);
});
