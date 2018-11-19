import React, { Component } from "react";
import PropTypes from "prop-types";
import { withStyles } from '@material-ui/core/styles';

const styles = theme => ({
  root: {
    flexGrow: 1,
  },
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
    return fetch(this.props.endpoint, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: this.props.username,
        password: this.props.password,
      }),
    })
    .then((response) => {
      if (!response.ok) {
        throw Error(response.statusText);
      }
      return response;
    })
    .then((response) => {
      return response.json();
    })
    .then((responseJson) => {
      const token = responseJson['token']; 
      if ( typeof(token) !== 'string' ) {
        throw Error("failed to get token from response json", responseJson);
      }
      this.setState(() => ({ authToken: token }));
      this.props.onChange(token);
    })
    .catch(error => {
      const msg = `An error occurred when getting auth token: ${error}`;
      console.error(msg, error);
      this.props.onError(msg);
    });
  }

  render() { return null; }
}

AuthTokenProvider.propTypes = {
  classes: PropTypes.object.isRequired,
  endpoint: PropTypes.string.isRequired,
  username: PropTypes.string.isRequired,
  password: PropTypes.string.isRequired,

  onError: PropTypes.func.isRequired,
  onChange: PropTypes.func.isRequired,
};

export default withStyles(styles)(AuthTokenProvider);
