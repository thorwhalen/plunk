


import React from "react";
import ReactDOM from "react-dom";
import FolderBrowser from "./FolderBrowser";

// Lots of import to define a Styletron engine and load the light theme of baseui
// import { Client as Styletron } from "styletron-engine-atomic";
// import { Provider as StyletronProvider } from "styletron-react";
// import { ThemeProvider, LightTheme } from "baseui";

// const engine = new Styletron();

// Wrap your CustomSlider with the baseui light theme
ReactDOM.render(
  <React.StrictMode>
    
        <FolderBrowser />
      
  </React.StrictMode>,
  document.getElementById("root")
);