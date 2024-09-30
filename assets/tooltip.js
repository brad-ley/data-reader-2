window.dccFunctions = window.dccFunctions || {};
window.dccFunctions.expTime = function (value) {
  return (10 ** (4 - value)).toFixed(0);
};
