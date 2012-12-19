/*  Django Foldable List-filter.
 *
 * https://bitbucket.org/Stanislas/django-foldable-list-filter
 *
 * Copyright 2012, Stanislas Guerra <stanislas.guerra@gmail.com>
 * Licensed under the BSD 2-Clause licence.
 * http://www.opensource.org/licenses/bsd-license.php
 *
 * */
(function($) {
    $(document).ready(function(){
        var foldable_list_filter = {
            filters: $("#changelist-filter h3"),
            cookie_name: "list_filter_closed",
            delim: "|",
            opened_class: "opened",
            transition_class: "schrodinger",
            closed_class: "closed",
            list_filter_closed: [],
            update_cookie: function(action, index) {
                if ($.isFunction($.cookie)) {
                    var list_filter_closed = foldable_list_filter.get_list_filter_closed();
                    if (action == foldable_list_filter.closed_class) {
                        list_filter_closed.push(index.toString());
                    } else {
                        list_filter_closed.splice(list_filter_closed.indexOf(index.toString()), 1);
                    }
                    $.cookie(foldable_list_filter.cookie_name,
                             list_filter_closed.join(foldable_list_filter.delim));
                }
            },
            get_list_filter_closed: function() {
                return ($.cookie(foldable_list_filter.cookie_name) || "")
                                             .split(foldable_list_filter.delim)
            }
        };

        if ($.isFunction($.cookie)) {
            foldable_list_filter.list_filter_closed = foldable_list_filter.get_list_filter_closed();
        }

        foldable_list_filter.filters.each(function(i, elt){
            var h3 = $(this);
            var statut_class = foldable_list_filter.opened_class;
            if (foldable_list_filter.list_filter_closed.indexOf(i.toString()) != -1) {
                statut_class = foldable_list_filter.closed_class;
            }
            h3.addClass("filter "+statut_class);
        });


        foldable_list_filter.filters.click(function(){
            var filter = $(this);
            filter.addClass(foldable_list_filter.transition_class);
            if ($(this).hasClass(foldable_list_filter.opened_class)) { // Closing.
                $(this).next().find('li:not(.selected)').slideUp(function(){
                    filter.removeClass(foldable_list_filter.transition_class+" "+
                                       foldable_list_filter.opened_class)
                          .addClass(foldable_list_filter.closed_class);
                });
                foldable_list_filter.update_cookie(
                        foldable_list_filter.closed_class,
                        foldable_list_filter.filters.index($(this))
                );
            } else { // Opening.
                $(this).next().find('li:not(.selected)').slideDown(function(){
                    filter.removeClass(foldable_list_filter.transition_class+" "+
                                       foldable_list_filter.closed_class)
                          .addClass(foldable_list_filter.opened_class);
                });
                foldable_list_filter.update_cookie(
                        foldable_list_filter.opened_class,
                        foldable_list_filter.filters.index($(this))
                );
            }
        });
    });

})(django.jQuery);