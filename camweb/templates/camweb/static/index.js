// var obj = document.getElementsByTagName('input')[0];
// obj.addEventListener('keydown', stopCarret); 
// obj.addEventListener('keyup', stopCarret); 

// function stopCarret() {
// 	if (obj.value.length > 5){
// 		setCaretPosition(obj, 4);
// 	}
// }

// function setCaretPosition(elem, caretPos) {
//     if(elem != null) {
//         if(elem.createTextRange) {
//             var range = elem.createTextRange();
//             range.move('character', caretPos);
//             range.select();
//         }
//         else {
//             if(elem.selectionStart) {
//                 elem.focus();
//                 elem.setSelectionRange(caretPos, caretPos);
//             }
//             else
//                 elem.focus();
//         }
//     }
// }