import React from "react";
import PropTypes from "prop-types";
import { withStyles } from "@material-ui/core/styles";
import Stepper from "@material-ui/core/Stepper";
import Step from "@material-ui/core/Step";
import StepLabel from "@material-ui/core/StepLabel";
import StepContent from "@material-ui/core/StepContent";
import Button from "@material-ui/core/Button";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import CardActions from "@material-ui/core/CardActions";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";

import QuerySequenceStep from "./QuerySequenceStep.js";
import FunfamMatchList from "./FunfamMatchList.js";
import ModelStructure from "./ModelStructure.js";
import SubmitCheckResultProvider from "./SubmitCheckResultProvider.js";

import { parseCathScanResponseData } from "../models/SearchScan.js";

import DummyCathScanResults from "../models/test_data/CathScanResults.test.json";

const STEP_QUERY = 0, STEP_TEMPLATE = 1, STEP_MODEL = 2;

const styles = theme => ({
  root: {
    width: "100%"
  },
  stepContent: {
    padding: theme.spacing(2),
  },
  button: {
    marginTop: theme.spacing(1),
    marginRight: theme.spacing(1),
  },
  actionsContainer: {
    marginBottom: theme.spacing(2)
  },
  resetContainer: {
    padding: theme.spacing(2)
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
      apiBase: "https://api01.cathdb.info/",
      authTokenEndpoint: "api/api-token-auth/",
      submitEndpoint: "api/select-template/",
      checkEndpoint: "api/select-template/<id>/",
      resultEndpoint: "api/select-template/<id>/results",
      taskIdFromSubmit: data => {
        return data["uuid"];
      },
      isCompleteFromCheck: data => {
        return data["status"] === "success";
      },
      isErrorFromCheck: data => {
        const msg = data["message"];
        return data["status"] === "error" ? msg : false;
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
      isErrorFromCheck: data => {
        return data["status"] === "error";
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
      templates: null,
      templateTaskId: null,
      hits: null,
      templateHitId: null,
      hitResult: null,
      templateModelId: null,
      modelResult: null,
      templateError: null,
      templateScanResult: null
    };

    this.handleSubmitSequence = this.handleSubmitSequence.bind(this);

    this.handleTemplateError = this.handleTemplateError.bind(this);
    this.handleTemplateSubmit = this.handleTemplateSubmit.bind(this);
    this.handleTemplateCheck = this.handleTemplateCheck.bind(this);
    this.handleTemplateResult = this.handleTemplateResult.bind(this);

    this.handleExampleScanResults = this.handleExampleScanResults.bind(this);

    // this.handleModelError = this.handleModelError.bind(this);
    // this.handleModelSubmit = this.handleModelSubmit.bind(this);
    // this.handleModelCheck = this.handleModelCheck.bind(this);
    // this.handleModelResult = this.handleModelResult.bind(this);
  }

  handleSubmitSequence(ev, seq) {
    console.log("Setting sequence: ", seq);
    const queryId = seq.id;
    const querySequence = seq.seq;
    this.setState(state => {
      return {
        activeStep: STEP_TEMPLATE,
        queryId: queryId,
        querySequence: querySequence,
        templateTaskId: null,
        hits: null,
        templateHitId: null,
        hitResult: null,
        templateModelId: null,
        modelResult: null,
      };
    });
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
      <QuerySequenceStep
        queryId={queryId}
        querySequence={querySeq}
        onSubmit={this.handleSubmitSequence}
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

  handleExampleScanResults(ev) {
    console.log("handleExampleScanResults");
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
      { label: "Submit Sequence", renderer: this.renderQuerySequence },
      { label: "Select Template", renderer: this.renderSelectTemplate },
      { label: "Model Structure", renderer: this.renderModelStructure },
    ];

    const stepContent = steps[activeStep].renderer.bind(this)();

    return (
      <div className={classes.root}>
        <Card>
          <CardContent>
            <Stepper activeStep={activeStep} alternativeLabel>
              {steps.map((step, index) => {
                const label = step["label"];
                const nextId = "next" + step["tag"];
                return (
                  <Step key={label}>
                    <StepLabel>{label}</StepLabel>
                  </Step>
                );
              })}
            </Stepper>
            <div className={classes.stepContent}>
              {stepContent}
            </div>
          </CardContent>
          <CardActions>
            {activeStep === steps.length && (
              <Paper square elevation={0} className={classes.resetContainer}>
                <Typography>All steps completed - you&quot;re finished</Typography>
                <Button onClick={this.handleReset} className={classes.button}>
                  Reset
                </Button>
              </Paper>
            )}
          </CardActions>
        </Card>
      </div>
    );
  }
}

WorkFlow.propTypes = {
  classes: PropTypes.object.isRequired
};

export default withStyles(styles)(WorkFlow);
