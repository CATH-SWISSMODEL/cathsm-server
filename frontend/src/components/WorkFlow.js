import React from "react";
import PropTypes from "prop-types";
import { withStyles } from "@material-ui/core/styles";
import Stepper from "@material-ui/core/Stepper";
import Step from "@material-ui/core/Step";
import StepLabel from "@material-ui/core/StepLabel";
import StepContent from "@material-ui/core/StepContent";
import Button from "@material-ui/core/Button";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";

import QuerySequence from "./QuerySequence.js";
import FunfamMatchList from "./FunfamMatchList.js";
import ModelStructure from "./ModelStructure.js";
import SubmitCheckResultProvider from "./SubmitCheckResultProvider.js";

import { parseCathScanResponseData } from "../models/SearchScan.js";

import DummyCathScanResults from "../models/test_data/CathScanResults.test.json"; 

const STEP_QUERY=0, STEP_TEMPLATE=1, STEP_MODEL=2;

const styles = theme => ({
  root: {
    width: "100%"
  },
  button: {
    marginTop: theme.spacing.unit,
    marginRight: theme.spacing.unit
  },
  actionsContainer: {
    marginBottom: theme.spacing.unit * 2
  },
  resetContainer: {
    padding: theme.spacing.unit * 3
  }
});

const STEPS_CONFIG = [
  {
    id: "query-sequence",
    label: "Query Sequence",
    dataClass: "QuerySequence"
  },
  {
    id: "select-template",
    label: "Select Template",
    resultClass: "SelectTemplateTable",
    providerClass: "SubmitCheckResultProvider",
    providerProps: {
      apiBase: "http://localhost:8000/",
      authTokenEndpoint: "api/api-auth-token/",
      submitEndpoint: "api/select-template/",
      checkEndpoint: "api/select-template/<id>/",
      resultEndpoint: "api/select-template/<id>/results",
      taskIdFromSubmit: data => {
        return data["uuid"];
      },
      isCompleteFromCheck: data => {
        return data["status"] === "success";
      },
      username: "apiuser",
      password: "apiuserpassword"
    },
    providerHandles: {
      onError: "handleTemplateError",
      onSubmitResponse: "handleTemplateSubmit",
      onCheckResponse: "handleTemplateCheck",
      onResultResponse: "handleTemplateResult"
    }
  },
  {
    id: "model-structure",
    label: "Model Structure",
    resultClass: "ModelStructure",
    providerClass: "SubmitCheckResultProvider",
    providerProps: {
      apiBase: "http://beta.swissmodel.expasy.org/",
      authTokenEndpoint: "api/api-auth-token/",
      submitEndpoint: "api/alignment/",
      checkEndpoint: "api/alignment/<id>/status",
      resultEndpoint: "api/alignment/<id>/",
      taskIdFromSubmit: data => {
        return data["uuid"];
      },
      isCompleteFromCheck: data => {
        return data["status"] === "success";
      },
      username: "ian",
      password: "4cathuse"
    },
    providerHandles: {
      onError: "handleModelError",
      onSubmitResponse: "handleModelSubmit",
      onCheckResponse: "handleModelCheck",
      onResultResponse: "handleModelResult"
    }
  }
];

// error
// {queryId, querySequence}: false => step1
// {queryId, querySequence}: true  => step1 complete

class WorkFlow extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      activeStep: 0,
      queryId: null,
      querySequence: null,
      taskId: null,
      templateError: null,
      templateScanResult: null
    };

    this.handleChangeSequence = this.handleChangeSequence.bind(this);
    this.handleTemplateError = this.handleTemplateError.bind(this);
    this.handleTemplateSubmit = this.handleTemplateSubmit.bind(this);
    this.handleTemplateCheck = this.handleTemplateCheck.bind(this);
    this.handleTemplateResult = this.handleTemplateResult.bind(this);

    this.handleExampleSequence = this.handleExampleSequence.bind(this);
    this.handleExampleScanResults = this.handleExampleScanResults.bind(this);

    // this.handleModelError = this.handleModelError.bind(this);
    // this.handleModelSubmit = this.handleModelSubmit.bind(this);
    // this.handleModelCheck = this.handleModelCheck.bind(this);
    // this.handleModelResult = this.handleModelResult.bind(this);
  }

  handleChangeSequence(queryId, querySequence) {
    console.log("Setting query sequence", queryId, querySequence);
    this.setState({ queryId, querySequence });
  }

  handleNext = e => {
    console.log("handleNext: ", e, e.target);
    this.setState(state => ({
      activeStep: state.activeStep + 1
    }));
  };

  handleBack = () => {
    this.setState(state => ({
      activeStep: state.activeStep - 1
    }));
  };

  handleReset = () => {
    this.setState({
      activeStep: 0
    });
  };

  renderQuerySequence() {
    const queryId = this.state.queryId;
    const querySeq = this.state.querySequence;
    return (
      <QuerySequence
        queryId={queryId}
        querySequence={querySeq}
        onChange={this.handleChangeSequence}
        onExampleScanResults={this.handleExampleScanResults}
        onExampleSequence={this.handleExampleSequence}
      />
    );
  }

  getStepConfigById(stepid) {
    return STEPS_CONFIG.find(data => data.id === stepid);
  }

  handleTemplateError(msg) {
    console.log("handleTemplateError", msg);
    this.setState({ templateError: true });
  }

  handleTemplateSubmit(data) {
    console.log("handleTemplateSubmit", data);
  }

  handleTemplateCheck(data) {
    console.log("handleTemplateCheck", data);
  }

  handleExampleSequence() {
    this.setState({

    })
  }

  handleExampleScanResults() {
    console.log("handleExampleScanResults", this);
    this.setState({
      activeStep: STEP_TEMPLATE,
      templateScanResult: DummyCathScanResults,
    });
  }

  handleTemplateResult(rawdata) {
    console.log("handleTemplateResult", rawdata);
    const scan = this.parseTemplateResultData(rawdata);
    if (scan.results.length > 1) {
      throw Error(
        `Scan has ${scan.results.length} results, expected exactly 1`
      );
    }
    const scanResult = scan.results[0];
    this.setState({ templateScanResult: scanResult });
  }

  parseTemplateResultData(rawdata) {
    console.log("parseTemplateResultData", rawdata);
    const results_json = rawdata.results_json;
    const data = JSON.parse(results_json);
    let scan = null;
    try {
      scan = parseCathScanResponseData(data);
    } catch (e) {
      console.log("failed to parse template results from data", e, rawdata);
      this.handleTemplateError("failed to parse template results from data");
    }
    console.log("parse: ", results_json, data.funfam_scan, scan);
    return scan;
  }

  renderSelectTemplate() {
    const stepConfig = this.getStepConfigById("select-template");
    const dataProps = stepConfig["providerProps"];

    const { queryId, querySequence, templateScanResult } = this.state;
    const templateSubmitData = {
      query_id: queryId,
      query_sequence: querySequence
    };
    let content;

    if (!templateScanResult) {
      content = (
        <SubmitCheckResultProvider
          {...dataProps}
          key="select-template"
          submitData={templateSubmitData}
          onError={this.handleTemplateError}
          onSubmitResponse={this.handleTemplateSubmit}
          onCheckResponse={this.handleTemplateCheck}
          onResultResponse={this.handleTemplateResult}
        />
      );
    } else {
      content = (
        <FunfamMatchList
          queryId={this.state.queryId}
          querySequence={this.state.queryId}
          scanResult={templateScanResult}
        />
      );
    }
    return <div>{content}</div>;
  }

  renderModelStructure() {
    return <ModelStructure />;
  }

  render() {
    const { classes } = this.props;
    const { activeStep } = this.state;
    const steps = [
      { label: "Query Sequence", content: this.renderQuerySequence() },
      { label: "Select Template", content: this.renderSelectTemplate() },
      { label: "Model Structure", content: this.renderModelStructure() }
    ];
    return (
      <div className={classes.root}>
        <Stepper activeStep={activeStep} orientation="vertical">
          {steps.map((step, index) => {
            const label = step["label"];
            const stepContent = step["content"];
            const nextId = "next" + step["tag"];
            return (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
                <StepContent>
                  {stepContent}
                  <div className={classes.actionsContainer}>
                    <div>
                      <Button
                        disabled={activeStep === 0}
                        onClick={this.handleBack}
                        className={classes.button}
                      >
                        Back
                      </Button>
                      <Button
                        variant="contained"
                        color="primary"
                        key={nextId}
                        onClick={this.handleNext}
                        className={classes.button}
                      >
                        {activeStep === steps.length - 1 ? "Finish" : "Next"}
                      </Button>
                    </div>
                  </div>
                </StepContent>
              </Step>
            );
          })}
        </Stepper>
        {activeStep === steps.length && (
          <Paper square elevation={0} className={classes.resetContainer}>
            <Typography>All steps completed - you&quot;re finished</Typography>
            <Button onClick={this.handleReset} className={classes.button}>
              Reset
            </Button>
          </Paper>
        )}
      </div>
    );
  }
}

WorkFlow.propTypes = {
  classes: PropTypes.object.isRequired
};

export default withStyles(styles)(WorkFlow);
