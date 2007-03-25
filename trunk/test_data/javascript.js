// Helper functions for managing site

dojo.require("dojo.widget.FisheyeList");
dojo.require("dojo.widget.TitlePane");
dojo.require("dojo.widget.SortableTable");
dojo.hostenv.writeIncludes();

function LoadContent(file){
    var docPane = dojo.widget.byId("docpane");
    if (!file){
	docPane.setContent("The desired link could not be found");
    }else{
	docPane.setUrl(file);
    }
}

function load_app(id){
    alert('Icon '+id+' was clicked');
}

function open_href(url){
    document.location.href = url;
}

