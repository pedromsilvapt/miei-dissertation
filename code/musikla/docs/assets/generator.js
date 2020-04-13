WebFont.load({
    google: {
      families: ['Amatic SC']
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

 function draw() {   
     function time ( ms ) {
       return ( ms / tl.duration );
     }

     function drawTimeline ( tl, label ) {
        const { x, y, width, height } = tl;
       
        // Bottom Line
        rc.line( x, y + height, x + width, y + height, { stroke: 'grey', roughtness: 1 } );
        // Left Line
        rc.line( x, y + height, x, y, { stroke: 'grey' } );
        // Right Line
        rc.line( x + width, y + height, x + width, y, { stroke: 'grey' } );

        ctx.textAlign = "center"
        ctx.font = "700 " + font_size + "px Amatic SC";
       
        ctx.fillText( label, x + width / 2, y + height + 60 );
    };
   
    function drawTimelineCells ( tl ) {
        const { x, y, width, height, total_length, cell_length } = tl;
      
        let cell_count = total_length / cell_length;
      
        let cell_width = width / cell_count;
      
        ctx.textAlign = "center"
        ctx.font = font_size + "px Amatic SC";
      
        for ( let i = 0; i <= cell_count; i++ ) {
          if ( i > 0 && i < cell_count ) {
            rc.line( x + i * cell_width, y + height * 1.1, x + i * cell_width, y + height * 0.25 );
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
      
      ctx.font = font_size + "px Amatic SC";
      ctx.textAlign="start";
      ctx.fillText( label, tl.x + offset, tl.y - tl.legend_top );
      
      offset += ctx.measureText( label ).width + tl.legend_padding_right
    }
   
    function drawLegend ( tl, color, label ) {
      rc.rectangle( tl.x + offset, tl.y - tl.legend_top - 17, 20, 20, { fill: color, stroke: color } )
      
      ctx.font = font_size + "px Amatic SC";
      ctx.textAlign="start";
      ctx.fillText( label, tl.x + offset + tl.legend_padding_left, tl.y - tl.legend_top );
      
      offset += tl.legend_padding_left + ctx.measureText( label ).width + tl.legend_padding_right
    }
   
    function drawTimelineMarker ( tl, start, end, color, label = null ) {
      const { x, y, width, height, total_length, cell_length } = tl;
      
      let cell_count = total_length / cell_length;
      
      let cell_width = width / cell_count;
      
      let start_x = width / ( total_length / start );
      let end_x = width / ( total_length / end );
      
      let rect_width = end_x - start_x;
      let rect_height = height * 0.5;
      
      rc.rectangle( 
        x + start_x, y + height - rect_height, rect_width, rect_height, 
        { roughness: 1, fill: color, stroke: color } 
      );
      
      if ( label  != null ) {
        drawLegend( tl, color, label )
      }
    }
   
   function drawTimelineEvent ( tl, pos, label, color = colors.grey ) {
      const { x, y, width, height, total_length, cell_length } = tl;
      
      let pos_x = width / ( total_length / pos );
     
      rc.line( tl.x + pos_x, tl.y + height * 1.1, tl.x + pos_x, tl.y, { stroke: color } )
      rc.line( tl.x + pos_x + 2, tl.y - 5, tl.x + pos_x + 15, tl.y - 5, { stroke: color } )
      
     
      ctx.font = "700 " + font_size + "px Amatic SC";
      ctx.textAlign="start";
      ctx.fillStyle=color;
      ctx.fillText( label, tl.x + pos_x + 23, tl.y + 2 );
   };

    var colors = {
      blue: 'rgb(62, 97, 162)',
      pink: 'rgb(194, 24, 91)',
      green: 'rgb(13, 144, 79)',
      orange: 'rgb(231, 76, 60)',
      grey: 'rgb(153, 153, 153)'
    };
   
    var width = 750, height = 210, margin = 10;
   
    var canvas = d3.select('#viz').append('canvas')
            .attr("id","canvas")
            .attr('width', width)
            .attr('height', height);
   
    var rc = rough.canvas(document.getElementById('canvas'));
	  var canvas = document.getElementById("canvas");
	  var ctx = canvas.getContext("2d");
   
    var font_size = 20;
    ctx.font = font_size + "px Amatic SC";
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
        
        drawTimelineEvent( tl, 1/8, "Event A", colors.grey );
        drawTimelineEvent( tl, 3/8, "Event B", colors.pink );
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
        
    drawExample4();

    // Colors: steelblue, seagreen, SlateBlue, RebeccaPurple, RoyalBlue
    
 }

  function save () {
    var canvas = document.getElementById("canvas");
    window.open(canvas.toDataURL('image/png'));
  }

// note = https://upload.wikimedia.org/wikipedia/commons/6/6f/Figure_rythmique_croche_hampe_haut.svg
