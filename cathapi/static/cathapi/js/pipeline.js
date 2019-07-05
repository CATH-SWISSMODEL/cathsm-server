var QUERY = {
  sequence: null,
  sequence_id: null,
};

(function ($) {
  "use strict"; // Start of use strict

  var stepper = new Stepper($(".bs-stepper")[0], {
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

  var forms = document.getElementsByClassName('needs-validation');
  // Loop over them and prevent submission
  var validation = Array.prototype.filter.call(forms, function (form) {
    form.addEventListener('submit', function (event) {
      console.log('checking form for validity: ', form, event, form.checkValidity());
      if (form.checkValidity() === false) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add('was-validated');
    }, false);
  });

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

  stepper.addEventListener('shown.bs-stepper', function (event) {
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
