#!/usr/bin/env ruby
=begin
  hudsonwidget-applet.rb
                                                                                
  Copyright (c) 2004 Ruby-GNOME2 Project Team
  This program is licenced under the same licence as Ruby-GNOME2.
                                                                     
=end

require 'gnomecanvas2'
require 'panelapplet2'
require 'gnome2'
require 'net/http'
require 'uri'
require 'rubygems'
require 'atom'
require 'gtk2'


class HudsonWidget < Gtk::EventBox
  Point = Struct.new("Point", :x, :y)
  class Point
    def to_p
     [x,y]
    end
    def -(p)
      [x-p.x, y-p.y]
    end
  end

  def setup()
    @tips = Gtk::Tooltips.new

    topleft = Point.new(5, 0.0)
    bottomright = Point.new(25.0, 20.0)
    center = Point.new(bottomright.x/2, bottomright.y/2)
    @face=Gnome::CanvasEllipse.new(@canvas.root, {
                 :x1 => topleft.x,
                 :y1 => topleft.y,
                 :x2 => bottomright.x,
                 :y2 => bottomright.y,
                 :fill_color => "steelblue",
                 :outline_color => "steelblue",
                 :width_pixels => 1})
   

  end

  def draw_hudsonwidget(resize=false)
    return false if destroyed?
    setup() unless defined?(@face)
	
    begin 
	    rssFeed = get_rss_feed(@feed)
	    buildDataHash = parse_rss_feed(rssFeed)
	    get_success_indicator(buildDataHash)
	
	rescue Exception => e
	    @tips.set_tip(self, "Cannot read RSS feed", nil)   
	    @face.set_fill_color("grey")
    end 
  end

  def set_feed(feed)
	@feed = feed
  end

  def set_intervall(time)
	@time = time
  end

  def initialize()
    super()

    @feed = "http://build.relis.lan:8000/hudson/rssLatest"
    @time = 300000

    set_border_width(@pad = 0)
    set_size_request((@width = 30)+(@pad*2), (@height = 100)+(@pad*2))
    @canvas = Gnome::Canvas.new(true)
    add @canvas
    draw_hudsonwidget(true)
    #set_bg(Gdk::Color.parse("#DA0006"))
    signal_connect('size-allocate') { |w,e,*b| 
      @width, @height = [e.width,e.height].collect{|i|i - (@pad*2)}
      @size = [@width,@height].min
      @radius = @size / 2
      @canvas.set_size(@width,@height)
      @canvas.set_scroll_region(0,0,@width,@height)
      draw_hudsonwidget(true)
      false
    }
    signal_connect_after('show') {|w,e| start() }
    signal_connect_after('hide') {|w,e| stop() } 
  end

  def show_window()
    @canvas.show()
    show()
  end


  def start
	@tid= Gtk::timeout_add(@time.to_i) { draw_hudsonwidget(); true }
  end
  def stop
	Gtk::timeout_remove(@tid) if @tid
	@tid = nil
  end
  def set_bg(bg)
  	modify_bg(Gtk::STATE_NORMAL, bg)
  	@canvas.modify_bg(Gtk::STATE_NORMAL, bg)
  end

  def get_rss_feed(feedUrl)
    feedXml = Net::HTTP::get(URI::parse(feedUrl))
    return Atom::Feed.new(feedXml)
  end


  def parse_rss_feed(rssFeed)
    buildList = []
    rssFeed.entries.each { |entry|
       buildLine = "#{entry.title} #{entry.published.strftime('%Y-%m-%d')}"
       buildName, buildNumber, buildStatus, buildDate = buildLine.split
       buildNumber = buildNumber[1..-1]
       buildStatus = buildStatus[1..-2]
       buildList += [[buildName, buildNumber, buildStatus, buildDate]]
    }

    buildDataHash = {}
    buildList.each { |buildData|
       buildName, buildNumber, buildStatus, buildDate = buildData

       if buildDataHash.member?(buildName)
          buildDataHash[buildName].addInfo(["#{buildNumber} #{buildStatus} #{buildDate}"])
       else
          buildDataHash[buildName] = BuildData.new
          buildDataHash[buildName].setName("#{buildName}")
          buildDataHash[buildName].setInfo(["#{buildNumber} #{buildStatus} #{buildDate}"])
       end
    }

    buildDataHash
  end

  def get_success_indicator(buildDataHash)
    success = true
    text = ''
    buildDataHash.each { |buildName, buildData|
      text += "#{buildName}: " + " #" + buildData.getInfo().first + "\n"
      if buildData.getInfo().first =~ /FAILURE/
         success = false
      end
      
    }
    
    @tips.set_tip(self, text, nil)
    
    if success
	@face.set_fill_color("green")
    else 
        @face.set_fill_color("red")
    end     
  end

end


class BuildData
  def initialize
    @buildName = ""
    @buildInfo = []
  end

  def setName(name)
    @name = name
  end

  def setInfo(info)
    @info = info
  end

  def addInfo(info)
    @info += info
  end

  def getInfo()
    return @info
  end

  def getName()
    return @name
  end

end


class ConfigReader

	def get_time()
		return @time
	end

	def set_time(time)
		@time = time
	end

	def get_feed()
		return @feed
	end

	def set_feed(feed)
		@feed = feed
	end

	def initialize() 
		@path = File.expand_path('~/.gnome2/hudson-applet')

		file = File.open(@path, File::RDONLY|File::CREAT)
		while file.gets do
			if $_ =~ /^TIME=(.*)$/
				set_time($1)
			end
			if $_ =~ /^URL=(.*)$/
				set_feed($1)
			end
		end
	end

	def is_configured()
		return false unless defined?@feed
		return false unless defined?@time
		return true
	end

	def write_setup()
		if is_configured
			file = File.open(@path, File::WRONLY|File::TRUNC|File::CREAT)
			file.puts "TIME="+@time.to_s
			file.puts "URL="+@feed
		end
	end

end

class InputDialog

	def enter_callback( entry )
		# Print the contents of the entry
		puts entry.text
	
		# Deletes the contents of the entry
		entry.delete_text( 0, -1 )
	end

	def set_feed( feed ) 
		@feed.set_text( feed )
	end

	def get_feed()
		return @feed.text
	end

	def set_time( time ) 
		@time.set_text( time )
	end

	def get_time() 
		return @time.text
	end

	def initialize()
		Gtk.init

		window = Gtk::Window.new( Gtk::Window::TOPLEVEL )
		window.set_default_size( 200, 100 )
		window.title=( "Ruby-GNOME2 Entry" )
		window.signal_connect( "destroy" ) { Gtk.main_quit }

		# Create a new vbox
		vbox = Gtk::VBox.new( false, 0 )
		window.add( vbox )
		vbox.show


		label = Gtk::Label.new("Hudson's RSS Feed:", true)
		vbox.pack_start( label, true, true, 0 )
		label.show

		@feed = Gtk::Entry.new
		@feed.set_max_length( 50 )
		@feed.set_text( "http://hudson.net/hudson/rssLatest" )
		@feed.select_region( 0, -1 )

		# Pack our @feed widget
		vbox.pack_start( @feed, true, true, 0 )
		@feed.show


		label = Gtk::Label.new("Check intervall in minutes:", true)
		vbox.pack_start( label, true, true, 0 )
		label.show

		@time = Gtk::Entry.new
		@time.set_max_length( 50 )
		@time.set_text( "5" )

		# Pack our Entry widget
		vbox.pack_start( @time, true, true, 0 )
		@time.show


		hbox = Gtk::HBox.new( false, 0 )
		vbox.add( hbox )
		hbox.show

		button = Gtk::Button.new( Gtk::Stock::QUIT )
		vbox.pack_start( button, true, true, 0 )
		button.signal_connect( "clicked" ) { 
			window.hide
			Gtk.main_quit 
		}
		button.set_flags( Gtk::Widget::CAN_DEFAULT )
		button.show
		button.grab_default
		
		window.show
	end

	def show()
		Gtk.main
	end
end

  config = ConfigReader.new
  if config.is_configured
	cfg_feed = config.get_feed
	cfg_time = config.get_time
  else 
	wd = InputDialog.new
	wd.set_feed("http://localhost:8000/hudson/rssLatest")
	wd.set_time("300000")
	wd.show
	cfg_feed = wd.get_feed
	cfg_time = wd.get_time
	config.set_time(wd.get_time)
	config.set_feed(wd.get_feed)
	config.write_setup
  end


OAFIID="OAFIID:GNOME_HudsonBuildApplet_Factory"

init = proc do |applet, iid|

  def vertical(applet)
#    applet.orient == Applet::ORIENT_LEFT || applet.orient == applet.ORIENT_RIGHT
   true    
  end

  def size(applet)
    if vertical applet
      applet.set_size_request(-1,applet.size-3)
    else
      applet.set_size_request(applet.size-3,-1)
    end
  end

  applet.signal_connect('change-size') { size(applet) }
  applet.signal_connect('change-orient') { size(applet) }
  size(applet)

  hudsonwidget = HudsonWidget.new
  hudsonwidget.set_feed(cfg_feed)
  hudsonwidget.set_intervall(cfg_time)
  hudsonwidget.show_window
  applet.add(hudsonwidget)
  applet.show_all
  
  true
end

oafiid = OAFIID
run_in_window = false
oafiid += "_debug" if run_in_window

PanelApplet.main(oafiid, "Hudson Build Indicator Applet (Ruby-GNOME2)", "0", &init)

if run_in_window
  main_window = Gtk::Window.new
  main_window.set_title "Hudson Build Indicator"
  main_window.signal_connect("destroy") { Gtk::main_quit }
  app = PanelApplet.new
  init.call(app, oafiid)
  app.reparent(main_window)
  main_window.show_all
  Gtk::main
end
