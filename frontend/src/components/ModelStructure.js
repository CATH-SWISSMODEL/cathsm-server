import React, { Component } from "react";
import PropTypes from "prop-types";
import { withStyles } from '@material-ui/core/styles';

const styles = theme => ({
    root: {
      flexGrow: 1,
      padding: theme.spacing.unit * 2,
    },
});
  
class ModelStructure extends Component {

    static propTypes = {
        apiBase: PropTypes.string.isRequired,
        submitEndpoint: PropTypes.string.isRequired,
        checkEndpoint: PropTypes.string.isRequired,
        resultsEndpoint: PropTypes.string.isRequired,
        checkTimeout: PropTypes.number.isRequired,
        checkMaxAttempts: PropTypes.number.isRequired,
        queryId: PropTypes.string.isRequired,
        querySequence: PropTypes.string.isRequired,
      };
    
    render() {
        const { data, loaded, placeholder } = this.state;
        return loaded ? data : <p>{placeholder}</p>;
    }
}

ModelStructure.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(ModelStructure);
