import { Component } from "react";
import PropTypes from "prop-types";
import { withStyles } from "@material-ui/core/styles";

const styles = theme => ({
  root: {
    flexGrow: 1
  }
});

class AuthTokenProvider extends Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  componentDidMount() {
    this.getAuthTokenAsync();
  }

  getAuthTokenAsync() {
    const data = {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        username: this.props.username,
        password: this.props.password
      })
    };

    return fetch(this.props.endpoint, data)
      .then(response => Promise.all([response.ok, response.json()]))
      .then(([responseOk, body]) => {
        if (responseOk) {
          const token = body["token"];
          if (typeof token !== "string") {
            throw Error("failed to get token from response json", body);
          }
          this.setState(() => ({ authToken: token }));
          this.props.onChange(token);
        } else {
          const msg = body["non_field_errors"]
            ? body["non_field_errors"]
            : "Unexpected error";
          throw Error(msg);
        }
      })
      .catch(error => {
        const msg = `Failed to get auth token: ${error}`;
        console.error(msg);
        this.props.onError(msg);
      });
  }

  render() {
    return null;
  }
}

AuthTokenProvider.propTypes = {
  classes: PropTypes.object.isRequired,
  endpoint: PropTypes.string.isRequired,
  username: PropTypes.string.isRequired,
  password: PropTypes.string.isRequired,

  onError: PropTypes.func.isRequired,
  onChange: PropTypes.func.isRequired
};

export default withStyles(styles)(AuthTokenProvider);
