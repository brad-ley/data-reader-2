window.dccFunctions = window.dccFunctions || {};
window.dccFunctions.expTime = function (value) {
  return (10 ** (5 - value)).toExponential(2);
};
