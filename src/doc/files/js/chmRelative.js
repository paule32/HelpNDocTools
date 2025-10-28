function relativelnk(a){
    // Simple path validation: allow only relative filenames (no slashes, no colon, no protocol)
    if (typeof a !== 'string' || a.match(/^[a-zA-Z0-9_.-]+$/) === null) {
        console.error('Invalid path for redirect');
        return;
    }
    var b, c;
    b = location.href.search(/:/)==2 ? 14 : 7;
    c = location.href.lastIndexOf("\\")+1;
   a = "file:///" + location.href.substring(b, c) + a;
   location.href = a;
};