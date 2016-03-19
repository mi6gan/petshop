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
      components: {
        src: 'src/scss/mini.basket.scss',
        dest: 'build/css/mini.basket.css'
      },
      bootstrap: {
        src: 'src/scss/bootstrap.scss',
        dest: 'build/vendor/css/bootstrap.css'
      },
      fontawesome: {
                src: 'node_modules/font-awesome/scss/font-awesome.scss',
                dest: 'build/vendor/font-awesome/css/font-awesome.css'
      }
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
    fontawesome: {
        files: [{
            expand: true,
            cwd: 'node_modules/font-awesome/fonts',
            src: ['**'], dest: 'build/vendor/font-awesome/fonts'}]
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
    vendorjs: {
        files: [{
            expand: true,
            cwd: 'src/vendor/js',
            src: ['**'], dest: 'build/vendor/js'}]
    },
    bootstrapjs: {
        files: [{
            expand: true,
            cwd: 'node_modules/bootstrap-sass/assets/javascripts/bootstrap',
            src: ['button.js', 'collapse.js', 'dropdown.js', 'transition.js', 'popover.js', 'tooltip.js', 'alert.js'],
            dest: 'build/vendor/js/bootstrap'}]
      },
    inputmask: {
        files: [{
            expand: true,
            cwd: 'node_modules/jquery.inputmask/dist/inputmask/',
            src: ['inputmask.js', 'inputmask.phone.extensions.js', 'jquery.inputmask.js'],
            dest: 'build/vendor/js/inputmask'}]
    },
    },
    watch: {
        sass: {
            files: ['src/scss/**'],
            tasks: ['sass:base', 'sass:components', 'sass:bootstrap']
        },
    	fonts: {
		    files: ['src/fonts/**'],
		    tasks: ['copy:fonts']
	    },
    	images: {
		    files: ['src/img/**'],
		    tasks: ['copy:images']
	    },
    	js: {
		    files: ['src/js/**'],
		    tasks: ['copy:js']
	    },
    }
  });

  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-sass');
  grunt.registerTask('default',['copy', 'sass']);

};
