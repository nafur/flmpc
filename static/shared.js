$.fn.dataTableExt.oApi.fnReloadAjax = function ( oSettings, sNewSource, fnCallback, bStandingRedraw )
{
    if ( typeof sNewSource != 'undefined' && sNewSource != null ) {
        oSettings.sAjaxSource = sNewSource;
    }
 
    // Server-side processing should just call fnDraw
    if ( oSettings.oFeatures.bServerSide ) {
        this.fnDraw();
        return;
    }
 
    this.oApi._fnProcessingDisplay( oSettings, true );
    var that = this;
    var iStart = oSettings._iDisplayStart;
    var aData = [];
  
    this.oApi._fnServerParams( oSettings, aData );
      
    oSettings.fnServerData.call( oSettings.oInstance, oSettings.sAjaxSource, aData, function(json) {
        /* Clear the old information from the table */
        that.oApi._fnClearTable( oSettings );
          
        /* Got the data - add it to the table */
        var aData =  (oSettings.sAjaxDataProp !== "") ?
            that.oApi._fnGetObjectDataFn( oSettings.sAjaxDataProp )( json ) : json;
          
        for ( var i=0 ; i<aData.length ; i++ )
        {
            that.oApi._fnAddData( oSettings, aData[i] );
        }
          
        oSettings.aiDisplay = oSettings.aiDisplayMaster.slice();
          
        if ( typeof bStandingRedraw != 'undefined' && bStandingRedraw === true )
        {
            oSettings._iDisplayStart = iStart;
            that.fnDraw( false );
        }
        else
        {
            that.fnDraw();
        }
          
        that.oApi._fnProcessingDisplay( oSettings, false );
          
        /* Callback user function - for event handlers etc */
        if ( typeof fnCallback == 'function' && fnCallback != null )
        {
            fnCallback( oSettings );
        }
    }, oSettings );
};

/*
 *	toggle css class for some id
 */
function toggleClass(id, data, cls) {
	if (data == 1) $(id).addClass(cls);
	else $(id).removeClass(cls);
}

/*
 *	build track string from track object
 */
function trackName(track) {
	if (track["Name"]) return track["Name"];
	if (track["Artist"] && track["Title"]) {
		if (track["Album"]) return track["Artist"] + " - " + track["Album"] + " - " + track["Title"];
		return track["Artist"] + " - " + track["Title"];
	}
	return track["file"];
}
function buildTrack(data, type, full) {
	return trackName(full);
}

/*
 *	format time below a day
 */
function formatTime(sec) {
	if (!sec) return "--";
	if (typeof sec == String) {
		if (sec.indexOf(":") > -1) sec = sec.substr(0, sec.indexOf(":"));
	}
	
	var sec = sec % (60*60*24) >> 0;

	var secs = sec % 60;
	if (secs < 10) secs = "0" + secs;
	sec = (sec - secs) / 60 >> 0;

	var mins = sec % 60;
	if (mins < 10) mins = "0" + mins;
	sec = (sec - mins) / 60 >> 0;
	
	if (sec > 0) return sec + ":" + mins + ":" + secs;
	else return mins + ":" + secs;
}

/*
 *	format time with weeks and days
 */
function formatLongTime(sec) {
	if (!sec) return "--";
	if (typeof sec == String) {
		if (sec.indexOf(":") > -1) sec = sec.substr(0, sec.indexOf(":"));
	}
	var res = "";
		
	if (sec > 60*60*24*7) {
		res += (sec / (60*60*24*7) >> 0) + "w ";
		sec %= 60*60*24*7;
	}
	if (sec > 60*60*24) {
		res += (sec / (60*60*24) >> 0) + "d ";
		sec %= 60*60*24;
	}
	res += formatTime(sec);

	return res;
}
