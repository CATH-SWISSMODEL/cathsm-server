import React, { Component } from "react";
import PropTypes from "prop-types";

class RemoteDataProvider extends Component {

  static defaultProps = {
    method: "GET",
  };

  constructor(props) {
    super(props);
    this.state = {};
  }

  componentDidMount() {
    console.log(`RemoteDataProvider().componentDidMount`);
    const interval = this.props.interval;
    this.timer = null;
    this.fetchData();
    if ( interval ) {
      console.log(`RemoteDataProvider().componentDidMount.setInterval`);
      this.timer = setInterval(() => this.fetchData(), interval);
    }
  }

  componentWillUnmount() {
    console.log('RemoteDataProvider().componentWillUnmount');
    clearInterval(this.timer);
  }

  fetchData() {
    const endpoint = this.props.endpoint;
    const authToken = this.props.authToken;
    const data = this.props.data;
    const method = this.props.method;

    let opts = {
      method,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      }
    };
    if ( authToken ) {
      opts.headers['Authorization'] = `token ${authToken}`;
    }
    if ( data ) {
      opts['body'] = JSON.stringify(data);
    }

    console.log(`Submitting data to ${endpoint}: method=${method}, auth=${authToken}, data=${data}`, opts);

    return fetch(endpoint, opts).then(response => {
      if (!response.ok) {
        throw Error(response.statusText);
      }
      return response;
    })
    .then(response => response.json())
    .then(responseJson => {
      console.log("fetchData.responseJson", responseJson);
      this.props.onComplete(responseJson);
    })
    .catch((error) => {
      const msg = `An error occurred when submitting sequence: ${error}`;
      this.props.onError(msg);
    });
  }

  render() { return null; }
}

RemoteDataProvider.propTypes = {
  endpoint: PropTypes.string.isRequired,
  method: PropTypes.string.isRequired,
  authToken: PropTypes.string,
  data: PropTypes.object,
  interval: PropTypes.number,
  onError: PropTypes.func.isRequired,
  onComplete: PropTypes.func.isRequired,
};

export default RemoteDataProvider;
