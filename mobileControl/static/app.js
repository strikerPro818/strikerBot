$(document).ready(function() {
  var joystick = new VirtualJoystick({
    container: document.getElementById('joystick'),
    mouseSupport: true,
    stationaryBase: true,
    baseX: 100,
    baseY: 100,
    limitStickTravel: true,
    stickRadius: 50
  });
  setInterval(function() {
    var angle = Math.round((joystick.deltaX() / 2) + 90);
    $('#angle').val(angle);
  }, 100);
});
