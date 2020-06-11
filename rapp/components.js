import * as React from "react"

export class Placeholder extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      active: false
    }
  }
  activate() {
    this.setState({ active: true })
  }
  render() {
    return (
      <div class="Instrument">
        {this.state.active && (
          <div>ACTIVE</div>
        )}
        {!this.state.active && (
          <div onClick={() => this.activate()}>Click here to activate</div>
        )}
      </div>
    )
  }
}
