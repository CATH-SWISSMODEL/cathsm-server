import React, { Component } from "react";
import PropTypes from "prop-types";
import { withStyles } from '@material-ui/core/styles';
import { Typography } from "@material-ui/core";

import CircularProgress from '@material-ui/core/CircularProgress';
import green from '@material-ui/core/colors/green';
import red from '@material-ui/core/colors/red';
import Button from '@material-ui/core/Button';
import CheckIcon from '@material-ui/icons/Check';
import SaveIcon from '@material-ui/icons/Save';

const styles = theme => ({
  root: {
    display: 'flex',
    alignItems: 'center',
  },
  wrapper: {
    margin: theme.spacing.unit,
    position: 'relative',
  },
});
  
class StepProgress extends Component {

  constructor(props) {
    super(props);
    this.state = {
      loading: false,
      success: false,
      error: false,
      message: 'No message',
    };
  }
    
  render() {
    const { loading, success, error, message } = this.state;
    const { classes } = this.props;

    return (
      <div className={classes.root}>
        <div className={classes.wrapper}>
        <Button
          variant="fab"
          color="primary"
          onClick={this.handleButtonClick}
        >
          {success ? <CheckIcon /> : <SaveIcon />}
        </Button>
        {loading && <CircularProgress size={68} />}
        </div>
      </div>
    );
  }
}

StepProgress.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(StepProgress);
