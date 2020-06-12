import * as React from "react"

import { listThings } from "./connectors"

export class Placeholder extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      things: []
    }
  }
  componentDidMount() {
    listThings().then((response) => {
      this.setState({ things: response.data.data });
    })
  }
  render() {
    return (
      <div>
        {this.state.things.map((ele) => (<li key={ele.text}>{ele.text}</li>))}
      </div>
    )
  }
}
