var QUERY = {
  sequence: null,
  sequence_id: null,
};

(function ($) {
  "use strict"; // Start of use strict

  var stepperEl = document.getElementById('cathsm-stepper');
  var stepper = new Stepper(stepperEl, {
    linear: false,
    animation: true,
  });

  var $input_sequence_id = $('#input-sequence-id');
  var $input_sequence = $('#input-sequence');
  var $stepper_status = $('#stepper-status');

  var showStatus = function (msg, style) {
    if (typeof style === 'undefined') {
      style = 'info';
    }
    $stepper_status.removeClass().addClass('alert alert-' + style).html(msg);
    setTimeout(function () {
      $stepper_status.alert('close');
    }, 5000);
  }

  var parseFasta = function (fasta_seq) {
    var id, seq;
    fasta_seq = $.trim(fasta_seq)
    if (!fasta_seq.startsWith('>')) {
      throw "expected FASTA formatted sequence to start with '>' (got: '" + fasta_seq.substr(0, 10) + "...')";
    }
    var fasta_lines = fasta_seq.split(/[\r\n]+/);
    var header = fasta_lines.shift();
    var sequence = fasta_lines.join('').replace(/\s+/, '');
    var header_matches = header.match(/^>(\S+)/)
    id = header_matches[1]
    return {
      id: id,
      seq: sequence,
    }
  }

  var handleSequencePaste = function (event) {
    var clipboardData, pastedData;

    // Stop data actually being pasted
    event.stopPropagation();
    event.preventDefault();

    // Get pasted data via clipboard API
    clipboardData = event.clipboardData || window.clipboardData || event.originalEvent.clipboardData;
    pastedData = clipboardData.getData('Text');

    pastedData = $.trim(pastedData);
    if (pastedData.startsWith('>')) {
      var seq = parseFasta(pastedData);
      $input_sequence_id.val(seq['id']);
      $input_sequence.val(seq['seq']);
      showStatus('Parsed FASTA sequence okay');
    }
    // Do whatever with pasteddata
  };


  // https://stackoverflow.com/a/21311717/821642

  function validateTextarea() {
    console.log("validateTextarea", this);
    var errorMsg = "Please match the format requested.";
    var textarea = this;
    var pattern = new RegExp('^' + $(textarea).attr('pattern') + '$');
    // check each line of text
    $.each($(this).val().split("\n"), function () {
      // check if the line matches the pattern
      var hasError = !this.match(pattern);
      console.log("match: ", this, pattern, this.match(pattern), hasError);
      if (typeof textarea.setCustomValidity === 'function') {
        textarea.setCustomValidity(hasError ? errorMsg : '');
      } else {
        // Not supported by the browser, fallback to manual error display...
        $(textarea).toggleClass('error', !!hasError);
        $(textarea).toggleClass('ok', !hasError);
        if (hasError) {
          $(textarea).attr('title', errorMsg);
        } else {
          $(textarea).removeAttr('title');
        }
      }
      return !hasError;
    });
  }

  $('.example-sequence').on('click', function (event) {
    var seq = $(this).data('sequence');
    var seq_id = $(this).data('sequenceId');
    $input_sequence.val(seq);
    $input_sequence_id.val(seq_id);
  })

  // Loop over forms and apply our own validation (prevent auto submission)
  var validateForm = function (event) {
    var $form = $(this);
    var formEl = $form[0];
    console.log('checking form for validity: ', formEl, $form.find('textarea'), event, formEl.checkValidity());
    $form.find('textarea[pattern]').each(validateTextarea);
    if (formEl.checkValidity() === false) {
      event.preventDefault();
      event.stopPropagation();
    }
    $form.addClass('was-validated');
  };

  $('form.needs-validation').each(function (idx, form) {
    $(form).on('submit', function (event) {
      validateForm(event);
    }, false);
  });

  $input_sequence.on('change keyup', validateForm);
  $input_sequence.on('paste', handleSequencePaste);

  $('.bs-stepper form').submit(function (event) {
    event.preventDefault();
    event.stopPropagation();
    console.log('stepper.next');
    stepper.next();
  });

  var submitSequence = function () {

  };

  var submitSelectedTemplate = function () {

  };

  stepperEl.addEventListener('shown.bs-stepper', function (event) {
    console.warn('step shown')

    switch (event.detail.indexStep) {
      case 1:
        submitSequence();
        break;
      case 2:
        submitSelectedTemplate();
        break;
      default:
        break;
    }
  });

})(jQuery); // End of use strict
