$(document).ready(function(){
  $('[data-toggle=offcanvas]').click(function(){
    var $this=$(this),
      target=$this.data('target');
    $(target).toggleClass('hidden-xs');
    $(target).toggleClass('hidden-sm');
  });

  $('.entry-content>table').addClass('table');
});

