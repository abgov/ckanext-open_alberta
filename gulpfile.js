'use strict';

var gulp = require('gulp');
var sass = require('gulp-sass');

gulp.task('sass', function () {
  return gulp.src('ckanext/open_alberta/sass/*.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest('ckanext/open_alberta/fanstatic/css'));
});

gulp.task('sass:watch', function () {
  gulp.watch('ckanext/open_alberta/sass/*.scss', ['sass']);
});
