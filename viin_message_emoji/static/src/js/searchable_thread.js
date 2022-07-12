odoo.define('viin_message_emoji.SearchableThread', function (require){
    "use strict";

    var SearchableThread = require('mail.model.SearchableThread');
    SearchableThread.include({
        updateCacheEmoji: function (props) {
            const {emoji_up, emoji_down, message_id} = props;
            //Update emoji on cache
            var cache = this._getCache([]);
            let indexMessage = -1;
            cache.messages.map((item, index)=>{
                if(item._id == message_id){
                    indexMessage = index;
                }
            })
            if(cache.messages[indexMessage].emoji==undefined){
                cache.messages[indexMessage].emoji = {
                    'total':0
                }
            }
            if(indexMessage!=-1){
                if(emoji_up!=false){
                    if(cache.messages[indexMessage].emoji[emoji_up]!=undefined){
                        cache.messages[indexMessage].emoji[emoji_up].number +=1;
                    }else{
                        cache.messages[indexMessage].emoji[emoji_up]={
                            name: emoji_up,
                            number: 1,
                        }
                    }
                    cache.messages[indexMessage].emoji.total +=1;
                }
                if(emoji_down!=false){
                    if(cache.messages[indexMessage].emoji[emoji_down]!=undefined){
                        cache.messages[indexMessage].emoji[emoji_down].number -=1;
                        if(cache.messages[indexMessage].emoji[emoji_down].number==0){
                            delete cache.messages[indexMessage].emoji[emoji_down];
                        }
                    }
                    cache.messages[indexMessage].emoji.total -=1;
                }
            }
        },
    });
    return SearchableThread;
})
