WebFont.load({
  google: {
    families: ['Amatic SC', 'Assistant', 'Lora']
  },
  active: function() {
    // dibujo solo si la tipografia 'Amatic SC' esta cargada
    draw();
  }
});

function fraction ( fr ) {
if ( ( fr.numerator / fr.denominator ) % 1 == 0 ) return fr.toString();

return "" + fr.numerator + "/" + fr.denominator;
}

function makeCurlyBrace(x1,y1,x2,y2,w,q)
{
//Calculate unit vector
var dx = x1-x2;
var dy = y1-y2;
var len = Math.sqrt(dx*dx + dy*dy);
dx = dx / len;
dy = dy / len;

//Calculate Control Points of path,
var qx1 = x1 + q*w*dy;
var qy1 = y1 - q*w*dx;
var qx2 = (x1 - .25*len*dx) + (1-q)*w*dy;
var qy2 = (y1 - .25*len*dy) - (1-q)*w*dx;
var tx1 = (x1 -  .5*len*dx) + w*dy;
var ty1 = (y1 -  .5*len*dy) - w*dx;
var qx3 = x2 + q*w*dy;
var qy3 = y2 - q*w*dx;
var qx4 = (x1 - .75*len*dx) + (1-q)*w*dy;
var qy4 = (y1 - .75*len*dy) - (1-q)*w*dx;

return ( "M " +  x1 + " " +  y1 +
        " Q " + qx1 + " " + qy1 + " " + qx2 + " " + qy2 + 
        " T " + tx1 + " " + ty1 +
        " M " +  x2 + " " +  y2 +
        " Q " + qx3 + " " + qy3 + " " + qx4 + " " + qy4 + 
        " T " + tx1 + " " + ty1 );
}

function draw() {   
   function time ( ms ) {
     return ( ms / tl.duration );
   }

   function drawTimeline ( tl, label ) {
      const { x, y, width, height } = tl;
     
      // Bottom Line
      rc.line( x, y + height, x + width, y + height, { stroke: 'grey', ...options } );
      // Left Line
      rc.line( x, y + height, x, y, { stroke: 'grey', ...options } );
      // Right Line
      rc.line( x + width, y + height, x + width, y, { stroke: 'grey', ...options } );

      ctx.textAlign = "center"
      ctx.font = font_heavy + " " + font_size + "px " + font_name;
      ctx.fillStyle="rgb(0, 0, 0)";
     
      ctx.fillText( label, x + width / 2, y + height + 60 );
  };
 
  function drawTimelineCells ( tl ) {
      const { x, y, width, height, total_length, cell_length } = tl;
    
      let cell_count = total_length / cell_length;
    
      let cell_width = width / cell_count;
    
      ctx.textAlign = "center"
      ctx.font = font_size + "px " + font_name;
      ctx.fillStyle="rgb(0, 0, 0)";
    
      for ( let i = 0; i <= cell_count; i++ ) {
        if ( i > 0 && i < cell_count ) {
          rc.line( x + i * cell_width, y + height * 1.1, x + i * cell_width, y + height * 0.25, { ...options } );
        }
        
        ctx.fillText( 
          fraction( new Fraction( cell_length * i ) ), 
          x + i * cell_width, y + height + 25 
        );
      }
  };
 
  let offset = 0;
  
  function drawLengthLegend ( tl ) {
    let cl = fraction( new Fraction( tl.cell_length ) );
    let dur = ( tl.duration * tl.cell_length ) / 1000;
    let label = cl + " = " + dur + ( dur == 1 ? "sec" : "secs" );
    
    ctx.font = font_normal + " " + font_size + "px " + font_name;
    ctx.textAlign="start";
    ctx.fillStyle="rgb(0, 0, 0)";
    ctx.fillText( label, tl.x + offset, tl.y - tl.legend_top );
    
    offset += ctx.measureText( label ).width + tl.legend_padding_right
  }
 
  function drawLegend ( tl, color, label ) {
    rc.rectangle( tl.x + offset, tl.y - tl.legend_top - 17, 20, 20, { fill: color, stroke: color, ...options } )
    
    ctx.font = font_normal + " " + font_size + "px " + font_name;
    ctx.textAlign="start";
    ctx.fillStyle="rgb(0, 0, 0)";
    ctx.fillText( label, tl.x + offset + tl.legend_padding_left, tl.y - tl.legend_top );
    
    offset += tl.legend_padding_left + ctx.measureText( label ).width + tl.legend_padding_right
  }
 
  function drawTimelineMarker ( tl, start, end, color, label = null, inlineLabel = null ) {
    const { x, y, width, height, total_length, cell_length } = tl;
    
    let cell_count = total_length / cell_length;
    
    let cell_width = width / cell_count;
    
    let start_x = width / ( total_length / start );
    let end_x = width / ( total_length / end );
    
    let rect_width = end_x - start_x;
    let rect_height = height * 0.5;
    
    rc.rectangle( 
      x + start_x, y + height - rect_height, rect_width, rect_height, 
      { fill: color, stroke: color, ...options } 
    );
    
    if ( label  != null ) {
      drawLegend( tl, color, label )
    }
    
    if ( inlineLabel != null ) {
      ctx.font = font_heavy + " " + font_size + "px " + font_name;
      ctx.textAlign="center";
      ctx.fillStyle=color;
      ctx.fillText( inlineLabel, x + start_x + ( rect_width / 2 ), y + + height - ( rect_height / 2 ) + ( font_size / 3 ) );
    }
  }
 
 function drawTimelineEvent ( tl, pos, label, color = colors.grey, rtl = false ) {
    rtl = rtl ? -1 : 1;
    
    const { x, y, width, height, total_length, cell_length } = tl;
    
    let pos_x = width / ( total_length / pos );
   
    rc.line( tl.x + pos_x, tl.y + height * 1.1, tl.x + pos_x, tl.y, { stroke: color, ...options } )
   
    rc.line( tl.x + pos_x + 2 * rtl, tl.y - 5, tl.x + pos_x + 15 * rtl, tl.y - 5, { stroke: color, ...options } )
    
   
    ctx.font = font_heavy + " " + font_size + "px " + font_name;
    ctx.textAlign = rtl == 1 ? "start" : "end";
    ctx.fillStyle = color;
    ctx.fillText( label, tl.x + pos_x + 23 * rtl, tl.y + 2 );
 };
 
 function drawTimelineBracket ( tl, label, start, end, color = colors.grey ) {
    const { x, y, width, height, total_length, cell_length } = tl;
    
    let cell_count = total_length / cell_length;
    
    let cell_width = width / cell_count;
    
    let start_x = width / ( total_length / start );
    let end_x = width / ( total_length / end );
    
    let rect_width = end_x - start_x;
    let rect_height = height * 0.5;
   
    const space = 4;
   
    const path = makeCurlyBrace( x + start_x + space, y + height + 5, x + end_x - space, y + height + 5, 20, 0.6);
   
    /*rc.rectangle( 
      x + start_x, y + height - rect_height, rect_width, rect_height, 
      { fill: color, stroke: color } 
    );*/
   
    rc.path( path, { color: color, stroke: color, ...options } );
   
    
   ctx.font = font_heavy + " " + font_size + "px " + font_name;
   ctx.textAlign = "center";
   ctx.fillStyle = color;
   ctx.fillText( label, x + start_x + ( rect_width / 2 ), y + height + 20 * 2 + ( font_size / 3 ) );
 }

  var colors = {
    blue: 'rgb(62, 97, 162)',
    pink: 'rgb(194, 24, 91)',
    green: 'rgb(13, 144, 79)',
    orange: 'rgb(231, 76, 60)',
    grey: 'rgb(153, 153, 153)'
  };
  
  const sketchy = false;
  var width = 750, height = 210, margin = 10;
  var options = {
    roughness: sketchy ? 1 : 0,
    bowing: sketchy ? 1 : 0,
    fillStyle: sketchy ? 'hachure' : 'dots',
    hachureGap: sketchy ? 4 : 10,
    strokeWidth: 2,
    fillWeight: 0.5
  };
 
 
  var canvas = d3.select('#viz').append('canvas')
          .attr("id","canvas")
          .attr('width', width)
          .attr('height', height);
 
  var rc = rough.canvas(document.getElementById('canvas'), options );
  var canvas = document.getElementById("canvas");
  var ctx = canvas.getContext("2d");
    
  var font_size = sketchy ? 20 : 16;
  var font_name = sketchy ? "Amatic SC" : "Assistant";
  var font_normal = sketchy ? "" : "400";
  var font_heavy = sketchy ? "700" : "800";
  ctx.font = font_normal + " " + font_size + "px " + font_name;
  ctx.textAlign="start";
 
  let tl = { 
      duration: 2000,
      total_length: 1,
      cell_length: 1 / 2,
      height: 60, 
      width: width - margin * 2,
      legend_padding_left: 27,
      legend_padding_right: 25,
      legend_top: 30
  };
  tl.y = height - margin * 3 - tl.height - 50;
  tl.x = margin;
 
    function drawExample0 () {
        drawTimeline( tl, "time" );
        drawLengthLegend( tl );
        drawTimelineMarker( tl, 1/2 - time( 1000 ), 1/2, colors.blue, "Range" );
        drawTimelineMarker( tl, 1/2 - time( 300 ) - time( 200 ), 1/2 + time( 300 ), colors.pink, "Forgiveness" );
        drawTimelineCells( tl );
        drawTimelineEvent( tl, 1/8, "Event A", colors.orange );
    }

    function drawExample1 () {
      // name: grids_default
    
      drawTimeline( tl, "time" );
      // drawLengthLegend( tl );
      drawTimelineMarker( tl, 0, 1/4, colors.blue, "Left" );
      drawTimelineMarker( tl, 1/4 , 1/2, colors.pink, "Right" );
      drawTimelineMarker( tl, 1/2, 3/4, colors.blue );
      drawTimelineMarker( tl, 3/4 , 1, colors.pink );
      drawTimelineCells( tl );
      drawTimelineEvent( tl, 1/8, "Event A", colors.blue );
      drawTimelineEvent( tl, 3/8, "Event B", colors.pink );
    }
 
    function drawExample2 () {
      // name: grids_direction_left
      drawTimeline( tl, "time" );
      // drawLengthLegend( tl );
      drawTimelineMarker( tl, 0, 1/2, colors.blue, "Left" );
      drawTimelineMarker( tl, 1/2, 1, colors.blue );
      drawTimelineCells( tl );
      drawTimelineEvent( tl, 1/8, "Event A", colors.blue );
      drawTimelineEvent( tl, 3/8, "Event B", colors.blue );
    }
 
    function drawExample3 () {
      // name: grids_ranges
      drawTimeline( tl, "time" );
      drawLengthLegend( tl );
      drawTimelineMarker( tl, 0, time(200), colors.blue, "Left" );
      drawTimelineMarker( tl, time(400), 1/2, colors.pink, "Right" );
      drawTimelineMarker( tl, 1/2, 1/2 + time(200), colors.blue );
      drawTimelineMarker( tl, 1/2 + time(400), 1, colors.pink );
      drawTimelineCells( tl );
      
      // drawTimelineEvent( tl, 1/8, "Event A", colors.grey );
      // drawTimelineEvent( tl, 3/8, "Event B", colors.pink );
    }
 
 
    function drawExample4 () {
      // name: grids_forgiveness
      drawTimeline( tl, "time" );
      drawLengthLegend( tl );
      drawTimelineMarker( tl, 0, 1/4, colors.blue, "Left" );
      drawTimelineMarker( tl, 1/4, 1/2 - time(300), colors.pink, "Right" );
      drawTimelineMarker( tl, 1/2, 3/4, colors.blue );
      drawTimelineMarker( tl, 3/4, 1 - time(300), colors.pink );
      drawTimelineCells( tl );
      
      drawTimelineEvent( tl, 1/8, "Event A", colors.blue );
      drawTimelineEvent( tl, 3/8, "Event B", colors.grey );
    }
 
    function drawExample5_1 () {
      // name: grids_recipe
      drawTimeline( tl, "time" );
      drawLengthLegend( tl );
      drawTimelineMarker( tl, 0, 1/2 - time(500), colors.blue, "Left" );
      drawTimelineMarker( tl, 1/2, 1 - time(500), colors.blue );
      drawTimelineCells( tl );
      
      drawTimelineEvent( tl, 1/8, "Event A", colors.blue );
      drawTimelineEvent( tl, 3/8, "Event B", colors.grey );
    }
 
    function drawExample5_2 () {
      // name: grids_recipe
      drawTimeline( tl, "time" );
      drawLengthLegend( tl );
      drawTimelineMarker( tl, 0, 1/2, colors.pink, "Right" );
      drawTimelineMarker( tl, 1/2, 1, colors.pink );
      drawTimelineCells( tl );
      
      drawTimelineEvent( tl, 0, "Event A", colors.grey );
      drawTimelineEvent( tl, 3/8, "Event B", colors.pink );
    }
 
 
    function drawExample6 () {
      // name: grids_forgiveness
      drawTimeline( tl, "time" );
      drawLengthLegend( tl );
      drawTimelineMarker( tl, 0, 1/4, colors.blue, "Left" );
      drawTimelineMarker( tl, 1/4, 1/2 - time(300), colors.pink, "Right" );
      drawTimelineMarker( tl, 1/2, 3/4, colors.blue );
      drawTimelineMarker( tl, 3/4, 1 - time(300), colors.pink );
      drawTimelineCells( tl );
      
      drawTimelineEvent( tl, 1/8, "Event A", colors.blue );
      drawTimelineEvent( tl, 3/8, "Event B", colors.grey );
    }
     
    function drawSchematics () {
      tl.total_length = 2;
      tl.cell_length = 1;
      
      colors.orange = 'rgb(254, 198, 18)'
      
      drawTimeline( tl, "time" );
      // drawLengthLegend( tl );
      // Right
      drawTimelineMarker( tl, 0, 1/8, colors.orange, "Forgiveness", "---" );
      drawTimelineMarker( tl, 1/8, 1/4 + 1/8, colors.green, "Range", "««" );
      drawTimelineMarker( tl, 3/8, 5/8, colors.grey, "Out of Range", "---" );
      
      drawTimelineBracket( tl, "right", 0, 4/8 );
      drawTimelineBracket( tl, "left", 4/8, 1 );
      
      drawTimelineBracket( tl, "right", 1, 12/8 );
      drawTimelineBracket( tl, "left", 12/8, 2 );
      
      // Left
      // drawTimelineMarker( tl, 1/2, 1/2 + 1/8, colors.grey, null, "---" );
      drawTimelineMarker( tl, 5/8, 5/8 + 1/4, colors.green, null, "»»" );
      drawTimelineMarker( tl, 7/8, 1, colors.orange, null, "---" );
      drawTimelineCells( tl );
      
      // Right
      drawTimelineMarker( tl, 1 + 0, 1 + 1/8, colors.orange, null, "---" );
      drawTimelineMarker( tl, 1 + 1/8, 1 + 1/4 + 1/8, colors.green, null, "««" );
      drawTimelineMarker( tl, 1 + 3/8, 1 + 5/8, colors.grey, null, "---" );
      
      // Right
      // drawTimelineMarker( tl, 1 + 1/2, 1 + 1/2 + 1/8, colors.grey, null, "---" );
      drawTimelineMarker( tl, 1 + 5/8, 1 + 5/8 + 1/4, colors.green, null, "»»" );
      drawTimelineMarker( tl, 1 + 7/8, 1 + 1, colors.orange, null, "---" );
      drawTimelineCells( tl );
      
      // drawTimelineEvent( tl, 1/8, "Event A", colors.blue );
      // drawTimelineEvent( tl, 3/8, "Event B", colors.grey );
    }
 
    function uminhoColors () {
      colors.red = '#a01e26';
      colors.orange = '#e36e1e';
      colors.orange = '#e36e1e';
      colors.blue = '#0079c0';
      colors.pink = '#c60651';
    }
 
    function drawDissertation1 () {
      tl.total_length = 2;
      tl.cell_length = 1;
      
      uminhoColors();
      
      drawTimeline( tl, "TEMPO" );
      // drawLengthLegend( tl );
      // Right
      drawTimelineMarker( tl, 0, 1, colors.orange, null, "Célula 1" );
      drawTimelineMarker( tl, 1, 2, colors.orange, null, "Célula 2" );
      
      drawTimelineBracket( tl, "DIREITA", 0, 4/8 );
      drawTimelineBracket( tl, "ESQUERDA", 4/8, 1 );
      
      drawTimelineBracket( tl, "DIREITA", 1, 12/8 );
      drawTimelineBracket( tl, "ESQUERDA", 12/8, 2 );
      
      drawTimelineCells( tl );
    }
 
    function drawDissertation2 () {
      tl.total_length = 1;
      tl.cell_length = 1;
      
      uminhoColors();
      
      // drawLengthLegend( tl );
      
      drawTimelineMarker( tl, 0, 1/8, colors.red, "Forgiveness", "---" );
      drawTimelineMarker( tl, 1/8, 1/4 + 1/8, colors.blue, "Range", "««" );
      
      drawTimelineBracket( tl, "DIREITA", 0, 4/8 );
      
      drawTimelineMarker( tl, 3/8, 5/8, colors.grey, "Out of Range", "---" );
      
      drawTimelineBracket( tl, "ESQUERDA", 4/8, 1 );
      
      drawTimelineMarker( tl, 5/8, 5/8 + 1/4, colors.blue, null, "»»" );
      drawTimelineMarker( tl, 7/8, 1, colors.red, null, "---" );
      
      drawTimeline( tl, "TEMPO" );
      drawTimelineCells( tl );
    }
 
    function drawDissertation3_1 () {
      tl.total_length = 2;
      tl.cell_length = 1;
      tl.duration = 1000;
      
      // name: grids_forgiveness
      drawTimeline( tl, "TEMPO" );
      drawLengthLegend( tl );
      // drawTimelineMarker( tl, 0, 1/8, colors.grey, "Out of range/Forgiveness" );
      drawTimelineMarker( tl, 1/8, 3/8, colors.blue, "Área Direita" );
      // drawTimelineMarker( tl, 3/8, 1 - 3/8, colors.grey );
      drawTimelineMarker( tl, 1 - 3/8, 1 - 1/8, colors.pink, "Área Esquerda" );
      // drawTimelineMarker( tl, 1 - 1/8, 1 + 1/8, colors.grey );
      
      
      drawTimelineMarker( tl, 1 + 1/8, 1 + 3/8, colors.blue );
      drawTimelineMarker( tl, 2 - 3/8, 2 - 1/8, colors.pink );
      
      // drawTimelineMarker( tl, 1/2, 3/4, colors.blue );
      // drawTimelineMarker( tl, 3/4, 1 - time(300), colors.pink );
      drawTimelineCells( tl );
      
      drawTimelineEvent( tl, 2/8, "Evento A", colors.blue );
      drawTimelineEvent( tl, 1 - 1/16, "Evento B", colors.grey );
      drawTimelineEvent( tl, 1 + 6/8, "Evento C", colors.pink );
    }
 
    function drawDissertation3_2 () {
      tl.total_length = 2;
      tl.cell_length = 1;
      tl.duration = 1000;
      
      // name: grids_forgiveness
      drawTimeline( tl, "TEMPO" );
      drawLengthLegend( tl );
      
      drawTimelineMarker( tl, 1/8, 3/8, colors.blue, "Mover para Esquerda" );
      drawTimelineMarker( tl, 1 - 3/8, 1 - 1/8, colors.pink, "Mover para Direita" );
      
      drawTimelineMarker( tl, 1 + 1/8, 1 + 3/8, colors.blue );
      drawTimelineMarker( tl, 2 - 3/8, 2 - 1/8, colors.pink );
      
      drawTimelineCells( tl );
      
      drawTimelineEvent( tl, 0, "Evento A", colors.blue );
      drawTimelineEvent( tl, 1 - 1/16, "Evento B", colors.grey );
      drawTimelineEvent( tl, 2, "Evento C", colors.pink, true );
    }
 
  uminhoColors();
  // drawExample6();
  drawDissertation3_2();

  // Colors: steelblue, seagreen, SlateBlue, RebeccaPurple, RoyalBlue
  
}

function save () {
  var canvas = document.getElementById("canvas");
  window.open(canvas.toDataURL('image/png'));
}

// note = https://upload.wikimedia.org/wikipedia/commons/6/6f/Figure_rythmique_croche_hampe_haut.svg
