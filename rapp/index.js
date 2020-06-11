import * as React from "react"
import { render } from "react-dom"
import { Placeholder } from "./components";
import "./components.css";

const App:React.SFC = () => <Placeholder/>;

render(<App/>, document.getElementById("root"));

if (module.hot) {
  module.hot.accept()
}
