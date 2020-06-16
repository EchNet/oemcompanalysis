import * as React from "react"

import { apiConnector } from "./connectors"

export class Placeholder extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      things: [],
      error: ""
    }
  }
  componentDidMount() {
    apiConnector.listThings()
      .then((response) => {
        this.setState({ things: response.data.data });
      })
      .catch((error) => {
        this.setState({ error: error.toString() });
      })
  }
  render() {
    if (this.state.error) {
      return (
        <div style={{ color: "red" }}>{this.state.error}</div>
      )
    }
    else {
      return (
        <div>
          {this.state.things.map((ele) => (<li key={ele.text}>{ele.text}</li>))}
        </div>
      )
    }
  }
}
