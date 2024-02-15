from django.contrib import admin

from puzzle import models


class ReadOnlyMixin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class KnightMoveAdmin(admin.ModelAdmin):
    change_list_template = 'admin/knight_move_change_list.html'
    exclude = ('puzzle_type',)
    readonly_fields = ('board', 'image')


class PieSliceAdmin(admin.ModelAdmin):
    change_list_template = 'admin/pie_slice_change_list.html'
    exclude = ('puzzle_type',)
    readonly_fields = ('obfuscated_word', 'image')


class WordFinderAdmin(admin.ModelAdmin):
    change_list_template = 'admin/word_finder_change_list.html'
    exclude = ('puzzle_type',)
    readonly_fields = ('board', 'image')


class WordTokenInline(admin.TabularInline):
    model = models.WordToken


class WordAdmin(admin.ModelAdmin):
    change_list_template = 'admin/word_change_list.html'
    list_filter = ('size',)
    readonly_fields = ('word',)
    inlines = (WordTokenInline,)
    search_fields = ('word',)


class WordSquareAdmin(ReadOnlyMixin, admin.ModelAdmin):
    change_list_template = 'admin/word_square_change_list.html'


class WordLadderAdmin(ReadOnlyMixin, admin.ModelAdmin):
    change_list_template = 'admin/word_ladder_change_list.html'


admin.site.register(models.KnightMove, KnightMoveAdmin)
admin.site.register(models.PieSlice, PieSliceAdmin)
admin.site.register(models.WordFinder, WordFinderAdmin)
admin.site.register(models.Word, WordAdmin)
admin.site.register(models.WordSquare, WordSquareAdmin)
admin.site.register(models.WordLadder, WordLadderAdmin)
