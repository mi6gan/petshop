module.exports = function(grunt) {

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    sass: {
      options: {
          sourceMap: true,
          includePaths: ['node_modules/bootstrap-sass/assets/stylesheets']
      },
      base: {
        src: 'src/scss/base.scss',
        dest: 'build/css/base.css'
      },
      bootstrap: {
        src: 'src/scss/bootstrap.scss',
        dest: 'build/vendor/css/bootstrap.css'
      },
    },
    copy: {
    images: {
		files: [
            {expand: true,
            cwd: 'src/images/',
            src: ['*.{png,jpg}'], dest: 'build/images'}
        ]
    },
    fonts: {
        files: [{
            expand: true,
            cwd: 'src/fonts/',
            src: ['*'],
            dest: 'build/fonts'}]
    },
    jquery: {
        src: 'node_modules/jquery/dist/jquery.min.js',
        dest: 'build/vendor/js/jquery.min.js'
    },
    js: {
        files: [{
            expand: true,
            cwd: 'src/js',
            src: ['**'], dest: 'build/js'}]
    },
    },
    watch: {
        sass: {
            files: ['src/scss/**'],
            tasks: ['sass:base', 'sass:bootstrap']
        },
    	fonts: {
		    files: ['src/fonts/**'],
		    tasks: ['copy:fonts']
	    },
    	images: {
		    files: ['src/img/**'],
		    tasks: ['copy:images']
	    },
    }
  });

  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-sass');
  grunt.registerTask('default',['copy', 'sass']);

};
