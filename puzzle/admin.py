from django.contrib import admin

from puzzle import models


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


class WordSquareAdmin(admin.ModelAdmin):
    change_list_template = 'admin/word_square_change_list.html'
    exclude = ('puzzle_type',)
    readonly_fields = ('board', 'solution', 'image', 'solution_image')


admin.site.register(models.KnightMove, KnightMoveAdmin)
admin.site.register(models.PieSlice, PieSliceAdmin)
admin.site.register(models.WordFinder, WordFinderAdmin)
admin.site.register(models.Word, WordAdmin)
admin.site.register(models.WordSquare, WordSquareAdmin)
