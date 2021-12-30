function imgchange(){
    var img = document.getElementById('img');
    var img1 = document.getElementById('img1');
    img.classList.toggle("img");
    img.classList.toggle("imgf");
    img1.classList.toggle("img1");
    img1.classList.toggle("img1f");
}
function movecurs(first,id){
    if(first.value.length){
        if (parseInt(id)<6){
            document.getElementById(('d'+(parseInt(id)+1)).toString()).focus();
        }
        if (parseInt(id)==6){
            
        }
    }
    else{
        console.log('hmm')
        if(parseInt(id)-1 >0){
            document.getElementById(('d'+(parseInt(id)-1)).toString()).focus()}
    }
}

function setcurs(id){
    ids = ['d1','d2','d3','d4','d5','d6']
    for(let i =0;i<parseInt(id);i++){
        var inp = document.getElementById(ids[i])
        if (inp.value.length){
            
        }
        else{
            inp.focus()
            break
        }
    }
}
function submitform(){
    var code = document.getElementById('code')
            for(let i=1;i<7;i++){
                code.value +=document.getElementById('d'+i.toString()).value
            }

}
function getCookie(cname) {
    let name = cname + "=";
    let ca = document.cookie.split(';');
    for(let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
}
function setCookie(cname, cvalue, exdays) {
    const d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    let expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}
// mode 0 light mode 1 dark
function toggleweb(){
    var mode = getCookie('mode')
    console.log(mode)
    if(parseInt(mode)){
        setlight()
        mode = 0
        setCookie('mode',mode)
    }
    else{
        setdark()
        mode = 1
        setCookie('mode',mode)
    }
}
// window.onload=function theme(){
//     var mode = getCookie('mode')
//     if (mode == ''){
//         mode = '0'
//     }
//     console.log(mode)
//     if(parseInt(mode)){
//         setdark()
//     }
// }
function setdark(){
        var body = document.getElementsByClassName('bodyl')
        var button = document.getElementsByClassName('buttonl')
        var input = document.getElementsByClassName('inputl')
        var dash = document.getElementsByClassName('splitterl')
        dash[0].classList.add('splitterd')
        dash[0].classList.remove('splitterl')  
        console.log('hmm1')
        for(let i=0;i<body.length;){
            body[i].classList.add('bodyd')
            body[i].classList.remove('bodyl')  
        }
        console.log('hmmm1')
        for(let i=0;i<button.length;){
            button[i].classList.add('buttond')
            button[i].classList.remove('buttonl')  
        }
        for(let i=0;i<input.length;){
            console.log(input.length)
            input[i].classList.add('inputd')
            input[i].classList.remove('inputl')  
        }
}
function setlight(){
        var body = document.getElementsByClassName('bodyd')
        var button = document.getElementsByClassName('buttond')
        var input = document.getElementsByClassName('inputd')
        var dash = document.getElementsByClassName('splitterd')
        dash[0].classList.add('splitterl')
        dash[0].classList.remove('splitterd')  
        console.log('hmm')
        for(let i=0;i<body.length;){
            body[i].classList.add('bodyl')
            body[i].classList.remove('bodyd')  
        }
        console.log('hmmm')
        for(let i=0;i<button.length;){
            button[i].classList.add('buttonl')
            button[i].classList.remove('buttond')  
        }

        for(let i=0;i<input.length;){
            console.log(input.length)
            input[i].classList.add('inputl')
            input[i].classList.remove('inputd')  
        }
}