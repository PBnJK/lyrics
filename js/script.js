/* Main script */

const DARK_THEME_TABLE = {
  "--text-primary": "#bbbbbb",
  "--text-secondary": "#959595",
  "--text-disabled": "#555555",

  "--bg-primary": "#181818",
  "--bg-secondary": "#343434",
  "--bg-highlight": "#223232",
  "--bg-info": "#113366",

  "--info-border": "#002244",
};

const LIGHT_THEME_TABLE = {
  "--text-primary": "#444444",
  "--text-secondary": "#6a6a6a",
  "--text-disabled": "#aaaaaa",

  "--bg-primary": "#e8e8e8",
  "--bg-secondary": "#cacaca",
  "--bg-highlight": "#cddddd",
  "--bg-info": "#88bbbb",

  "--info-border": "#668888",
};

const root = document.querySelector(":root");

const getCurrentTheme = () => {
  const attr = "--text-primary";
  const curColor = getComputedStyle(root).getPropertyValue(attr);

  return curColor == LIGHT_THEME_TABLE[attr] ? "light" : "dark";
};

const setCurrentTheme = (table) => {
  for (const key in table) {
    root.style.setProperty(key, table[key]);
  }
};

const themeButton = document.getElementById("theme-button");
themeButton.addEventListener("click", () => {
  const curTheme = getCurrentTheme();

  if (curTheme === "dark") {
    setCurrentTheme(LIGHT_THEME_TABLE);
    themeButton.innerText = "Light";
    sessionStorage.setItem("theme", "light");
  } else {
    setCurrentTheme(DARK_THEME_TABLE);
    themeButton.innerText = "Dark";
    sessionStorage.setItem("theme", "dark");
  }
});

if (sessionStorage.getItem("theme") === "dark") {
  setCurrentTheme(DARK_THEME_TABLE);
  themeButton.innerText = "Dark";
} else {
  setCurrentTheme(LIGHT_THEME_TABLE);
  themeButton.innerText = "Light";
}
