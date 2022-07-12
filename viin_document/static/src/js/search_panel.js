odoo.define('viin_document/static/src/js/search_panel.js', function(require){
    "use strict"

    const SearchPanel  = require("web/static/src/js/views/search_panel.js");

    SearchPanel.patch("viin_document.SearchPanel", (T) => {
        class SearchPanelPatchDocument extends T {
            mounted(){
                this._updateGroupHeadersChecked();
                if (this.hasImportedState) {
                    this.el.scroll({ top: this.scrollTop });
                }
                if(this.model.config.modelName == 'document.document'){
                    let _active_el = $(this.el).find('.list-group-item-action.active')
                    if(_active_el.length){
                        _active_el[0].scrollIntoView({block: "center", inline: "nearest"});
                    }
                }
            }
        }
        return SearchPanelPatchDocument;
    })

})
